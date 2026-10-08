#!/usr/bin/env python3
"""Validate a completed N100 capture and emit a hash manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path


REQUIRED_FILES = (
    "witness.pcap",
    "witness-events.jsonl",
    "witness-meta.json",
    "tcpdump-stderr.txt",
)


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def validate_capture(root: Path) -> dict:
    missing = [name for name in REQUIRED_FILES if not (root / name).is_file()]
    if missing:
        raise RuntimeError(f"capture evidence incomplete; missing: {', '.join(missing)}")

    pcap = root / "witness.pcap"
    if pcap.stat().st_size <= 24:
        raise RuntimeError("pcap contains no packet payload; refusing to manifest it")

    try:
        meta = json.loads((root / "witness-meta.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("witness-meta.json is unreadable or invalid JSON") from exc

    if meta.get("schema") != "p347-n100-witness-v2":
        raise RuntimeError("unsupported or missing witness metadata schema")
    if not meta.get("actor_ip") or not meta.get("target_ips") or not meta.get("target_host"):
        raise RuntimeError("actor/target provenance is incomplete")
    if meta.get("target_ip_source") != "Mac-side application/socket trace":
        raise RuntimeError("target IP provenance must come from the Mac-side trace")

    expected_hashes = {
        "witness.pcap": "pcap_sha256",
        "witness-events.jsonl": "events_sha256",
        "tcpdump-stderr.txt": "tcpdump_stderr_sha256",
    }
    for filename, key in expected_hashes.items():
        observed = digest(root / filename)
        if meta.get(key) != observed:
            raise RuntimeError(f"{filename} SHA-256 does not match witness metadata")

    event_path = root / "witness-events.jsonl"
    try:
        events = [
            json.loads(line)
            for line in event_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("witness-events.jsonl is unreadable or invalid JSONL") from exc

    if len(events) < 2 or events[0].get("event") != "capture_start" or events[-1].get("event") != "capture_stop":
        raise RuntimeError("capture event stream lacks matching start/stop boundaries")
    if events[-1].get("exited_before_duration") is not False:
        raise RuntimeError("tcpdump exited before the requested capture duration")
    if events[-1].get("returncode") not in (0, 130, -2):
        raise RuntimeError("tcpdump did not finish with an accepted return code")
    if events[0].get("actor_ip") != meta.get("actor_ip"):
        raise RuntimeError("actor IP differs between event stream and metadata")
    if events[0].get("target_ips") != meta.get("target_ips"):
        raise RuntimeError("target IP set differs between event stream and metadata")

    return meta


def build_manifest(directory: str | Path) -> Path:
    root = Path(directory).expanduser().resolve()
    if not root.is_dir():
        raise RuntimeError(f"capture directory does not exist: {root}")
    if (root / "manifest.json.tmp").exists():
        raise RuntimeError("stale manifest.json.tmp exists; preserve and inspect the directory")
    validate_capture(root)

    files = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name not in ("manifest.json", "manifest.json.tmp"):
            files.append({
                "path": str(path.relative_to(root)),
                "sha256": digest(path),
                "size": path.stat().st_size,
            })

    output = root / "manifest.json"
    temporary = root / "manifest.json.tmp"
    with temporary.open("x", encoding="utf-8") as stream:
        json.dump({"schema": "p347-n100-witness-manifest-v2", "files": files}, stream, indent=2, sort_keys=True)
        stream.write("\n")
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temporary, output)
    directory_fd = os.open(root, os.O_RDONLY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)
    return output


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory")
    args = parser.parse_args()
    print(build_manifest(args.directory))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
