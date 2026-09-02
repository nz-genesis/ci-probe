#!/usr/bin/env python3
"""Verify a frozen SHA-256 commitment for an independent replication.

Commitment format:
  SHA256(raw_submission_bytes + b"\n" + nonce_utf8)

The raw submission is intentionally opaque to this verifier. This tool checks
integrity and challenge binding only; it does not evaluate semantic content.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def digest(raw: bytes, nonce: str) -> str:
    return sha256(raw + b"\n" + nonce.encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify an independent replication commitment")
    parser.add_argument("commitment", type=Path, help="commitment JSON")
    parser.add_argument("submission", type=Path, help="frozen raw submission")
    parser.add_argument("nonce", help="nonce used when commitment was created")
    parser.add_argument("--challenge", required=True, type=Path, help="exact frozen challenge bytes")
    args = parser.parse_args()

    commitment = json.loads(args.commitment.read_text(encoding="utf-8"))
    required = {"protocol", "challenge_sha256", "submission_sha256", "hash_algorithm"}
    missing = required - commitment.keys()
    if missing:
        raise SystemExit(f"missing commitment fields: {sorted(missing)}")
    if commitment["protocol"] != "genesis-independent-replication-v1":
        raise SystemExit("unsupported protocol")
    if commitment["hash_algorithm"] != "SHA-256(raw_submission_bytes + newline + nonce_utf8)":
        raise SystemExit("unsupported hash algorithm")

    challenge_bytes = args.challenge.read_bytes()
    actual_challenge_sha = sha256(challenge_bytes)
    if commitment["challenge_sha256"] != actual_challenge_sha:
        raise SystemExit("challenge hash mismatch")

    raw = args.submission.read_bytes()
    actual = digest(raw, args.nonce)
    if actual != commitment["submission_sha256"]:
        raise SystemExit("submission commitment mismatch")

    print("COMMITMENT VERIFIED")
    print(f"challenge_sha256={actual_challenge_sha}")
    print(f"submission_sha256={actual}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
