#!/usr/bin/env python3
"""Independent P347 packet witness; records packets and provenance only."""
from __future__ import annotations

import argparse
import hashlib
import ipaddress
import json
import os
import shutil
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def append_event(path: Path, event: str, **fields) -> None:
    record = {
        "event": event,
        "wall_time_utc": utc_now(),
        "monotonic_ns": time.monotonic_ns(),
        "pid": os.getpid(),
        **fields,
    }
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
        stream.flush()
        os.fsync(stream.fileno())


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def normalize_ip(value: str, label: str = "IP address") -> str:
    try:
        return str(ipaddress.ip_address(value))
    except ValueError as exc:
        raise ValueError(f"{label} must be a literal IPv4/IPv6 address: {value!r}") from exc


def build_capture_filter(actor_ip: str, target_ips: list[str], target_port: int) -> str:
    if not isinstance(target_port, int) or not 1 <= target_port <= 65535:
        raise ValueError("target port must be an integer from 1 to 65535")
    actor = normalize_ip(actor_ip, "actor IP")
    targets = sorted({normalize_ip(value, "target IP") for value in target_ips})
    if not targets:
        raise ValueError("at least one target IP from the Mac-side trace is required")
    target_expression = " or ".join(f"host {value}" for value in targets)
    return f"host {actor} and ({target_expression}) and port {target_port}"


def require_empty_directory(path: str | Path) -> Path:
    output = Path(path).expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        raise RuntimeError(
            f"capture directory must be empty; use a new run-specific directory: {output}"
        )
    return output


def write_json_durable(path: Path, value: dict) -> None:
    temporary = path.with_name(path.name + ".tmp")
    with temporary.open("x", encoding="utf-8") as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, path)
    directory_fd = os.open(path.parent, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--interface", required=True)
    parser.add_argument("--capture-dir", required=True)
    parser.add_argument("--target-host", required=True, help="authority hostname for provenance")
    parser.add_argument(
        "--actor-ip",
        required=True,
        help="Mac actor IP as visible on the N100 capture interface",
    )
    parser.add_argument(
        "--target-ip",
        action="append",
        required=True,
        help="actual remote IP from the Mac-side trace; repeat for each observed IP",
    )
    parser.add_argument("--target-port", type=int, default=443)
    parser.add_argument("--duration", type=int, default=300)
    args = parser.parse_args()

    if args.duration < 1:
        raise ValueError("duration must be at least one second")

    actor_ip = normalize_ip(args.actor_ip, "actor IP")
    target_ips = sorted({normalize_ip(value, "target IP") for value in args.target_ip})
    capture_filter = build_capture_filter(actor_ip, target_ips, args.target_port)

    tcpdump = shutil.which("tcpdump")
    if tcpdump is None:
        raise RuntimeError("tcpdump is required")

    output = require_empty_directory(args.capture_dir)
    events = output / "witness-events.jsonl"
    pcap = output / "witness.pcap"
    metadata = output / "witness-meta.json"
    stderr_path = output / "tcpdump-stderr.txt"

    append_event(
        events,
        "capture_start",
        interface=args.interface,
        actor_ip=actor_ip,
        target_host=args.target_host,
        target_port=args.target_port,
        target_ips=target_ips,
        target_ip_source="Mac-side application/socket trace",
        duration_seconds=args.duration,
        tcpdump_filter=capture_filter,
    )

    with stderr_path.open("x", encoding="utf-8") as stderr_file:
        process = subprocess.Popen(
            [
                tcpdump,
                "-i",
                args.interface,
                "-nn",
                "-s",
                "0",
                "-w",
                str(pcap),
                capture_filter,
            ],
            stdout=subprocess.DEVNULL,
            stderr=stderr_file,
            text=True,
        )
        started = time.monotonic()
        deadline = started + args.duration
        early_exit = False
        try:
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    early_exit = True
                    break
                time.sleep(min(0.25, max(0.0, deadline - time.monotonic())))
        finally:
            if process.poll() is None:
                try:
                    process.send_signal(signal.SIGINT)
                except ProcessLookupError:
                    pass
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=5)

    elapsed = time.monotonic() - started
    return_code = process.returncode
    append_event(
        events,
        "capture_stop",
        returncode=return_code,
        elapsed_seconds=round(elapsed, 3),
        exited_before_duration=early_exit,
    )

    if early_exit:
        raise RuntimeError(
            f"tcpdump exited before the requested duration (return code {return_code}); "
            f"inspect {stderr_path}"
        )
    if return_code not in (0, 130, -signal.SIGINT):
        raise RuntimeError(
            f"tcpdump failed with return code {return_code}; inspect {stderr_path}"
        )
    if not pcap.exists() or pcap.stat().st_size <= 24:
        raise RuntimeError("tcpdump produced no packet payload; capture is not admissible")

    meta = {
        "schema": "p347-n100-witness-v2",
        "host": os.uname().nodename,
        "interface": args.interface,
        "actor_ip": actor_ip,
        "target_host": args.target_host,
        "target_port": args.target_port,
        "target_ips": target_ips,
        "target_ip_source": "Mac-side application/socket trace",
        "tcpdump_filter": capture_filter,
        "requested_duration_seconds": args.duration,
        "observed_elapsed_seconds": round(elapsed, 3),
        "tcpdump_returncode": return_code,
        "pcap_sha256": sha256(pcap),
        "events_sha256": sha256(events),
        "tcpdump_stderr_sha256": sha256(stderr_path),
    }
    write_json_durable(metadata, meta)
    print(f"pcap={pcap}")
    print(f"pcap_sha256={meta['pcap_sha256']}")
    print(f"events_sha256={meta['events_sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
