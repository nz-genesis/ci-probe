#!/usr/bin/env python3
"""Bounded read-only readiness check for the P347 temporary authority route."""
import argparse
import json
import os
import subprocess
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path

from actor import request
from visibility_discovery import sanitize_result

TRANSIENT_EDGE = {(404, 1042), (500, 1104)}


def utc():
    return datetime.now(timezone.utc).isoformat()


def is_transient(result):
    body = result.get("response_body")
    body = body if isinstance(body, dict) else {}
    status = result.get("http_status")
    return (
        result.get("transport_state") == "UNKNOWN"
        or status == 523
        or (status, body.get("error_code")) in TRANSIENT_EDGE
    )


def one_probe(url, expected_source, request_fn=request, sleep_fn=time.sleep,
              max_attempts=30, interval_seconds=2):
    correlation_id = str(uuid.uuid4())
    attempts = []
    for number in range(1, max_attempts + 1):
        result = sanitize_result(request_fn(
            url.rstrip("/") + "/v1/state",
            method="GET",
            headers={"X-Correlation-ID": correlation_id},
            timeout=10.0,
        ))
        result.update({"attempt": number, "correlation_id": correlation_id})
        body = result.get("response_body")
        body = body if isinstance(body, dict) else {}
        valid = (
            result.get("http_status") == 200
            and result.get("transport_state") == "HTTP_RESPONSE_OBSERVED"
            and body.get("authority") == "P347_EXTERNAL_AUTHORITY"
            and body.get("source_version") == expected_source
            and bool(result.get("local_ip"))
            and bool(result.get("remote_ip"))
        )
        attempts.append({"result": result, "valid": valid})
        if valid:
            return attempts, True, None
        # Do not retry arbitrary HTTP errors (especially 401/403 challenges).
        if number >= max_attempts or not is_transient(result):
            if result.get("http_status") == 200 and body.get("source_version") != expected_source:
                error = "authority source_version mismatch"
            elif result.get("http_status") == 200 and body.get("authority") != "P347_EXTERNAL_AUTHORITY":
                error = "authority identity mismatch"
            elif result.get("http_status") == 200 and (not result.get("local_ip") or not result.get("remote_ip")):
                error = "curl did not report local_ip and remote_ip"
            else:
                error = "read-only authority readiness probe failed closed"
            return attempts, False, error
        sleep_fn(interval_seconds)
    return attempts, False, "bounded readiness retry budget exhausted"


def checkout_sha():
    root = Path(__file__).resolve().parents[2]
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root,
        capture_output=True, text=True, check=False,
    )
    if result.returncode:
        raise RuntimeError("cannot establish exact checkout SHA")
    return result.stdout.strip()


def write_evidence(path, evidence):
    path = Path(path).expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("w", encoding="utf-8") as stream:
        json.dump(evidence, stream, ensure_ascii=False, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    temporary.replace(path)
    path.chmod(0o600)


def run(args, request_fn=request, sleep_fn=time.sleep):
    url = Path(args.authority_url_file).expanduser().read_text(encoding="utf-8").strip().rstrip("/")
    if not url.startswith("https://") or ".workers.dev" not in url:
        raise RuntimeError("authority URL must be an HTTPS workers.dev URL, not a claim URL")
    actual_sha = checkout_sha()
    if actual_sha != args.actor_source_version:
        raise RuntimeError("readiness checkout SHA does not match expected actor source SHA")
    evidence = {
        "schema": "p347-authority-readiness-v1",
        "observed_at_utc": utc(),
        "actor_source_version": actual_sha,
        "authority_source_version_expected": args.expected_source_version,
        "authority_url": url,
        "readiness": "PENDING",
        "attempts": [],
        "result": "PENDING",
    }
    attempts, ready, error = one_probe(
        url, args.expected_source_version, request_fn, sleep_fn,
        max_attempts=args.max_attempts, interval_seconds=args.interval_seconds,
    )
    evidence["attempts"] = [entry["result"] for entry in attempts]
    evidence["readiness"] = "READY" if ready else "FAILED_CLOSED"
    evidence["result"] = "PASS" if ready else "FAIL"
    evidence["error"] = error
    evidence["completed_at_utc"] = utc()
    write_evidence(args.output, evidence)
    print(json.dumps({
        "result": "P347_AUTHORITY_READINESS_" + evidence["result"],
        "ready": ready,
        "attempt_count": len(attempts),
        "http_status": attempts[-1]["result"].get("http_status") if attempts else None,
        "remote_ip": attempts[-1]["result"].get("remote_ip") if attempts else None,
        "error": error,
        "evidence": str(Path(args.output).expanduser()),
    }, sort_keys=True), flush=True)
    return 0 if ready else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authority-url-file", required=True)
    parser.add_argument("--expected-source-version", required=True)
    parser.add_argument("--actor-source-version", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-attempts", type=int, default=30)
    parser.add_argument("--interval-seconds", type=int, default=2)
    args = parser.parse_args()
    if not 1 <= args.max_attempts <= 30:
        parser.error("max-attempts must be in 1..30")
    if not 0 <= args.interval_seconds <= 10:
        parser.error("interval-seconds must be in 0..10")
    try:
        return run(args)
    except Exception as exc:
        print("P347_AUTHORITY_READINESS_ERROR=" + type(exc).__name__ + ": " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
