#!/usr/bin/env python3
"""Fail-closed validation for an IR-V3 blind-run bundle.

This validates bundle integrity only. It does not establish semantic adequacy,
material external independence, or target agreement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_CHALLENGE_ID = "IR-V3"
EXPECTED_SCHEMA_VERSION = "3.0.0"
EXPECTED_CHALLENGE_SHA256 = "913c162ede3741ead44dca3efe3fbbf33f5de764254d6a2da88cc90cf08b05a"
EXPECTED_EPISTEMIC_STATUS = "RAW_BLIND_RUN"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def commitment(raw: bytes, nonce: str) -> str:
    return sha256_bytes(raw + b"\n" + nonce.encode("utf-8"))


def fail(message: str) -> None:
    raise SystemExit(f"INVALID: {message}")


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON in {path.name}: {type(exc).__name__}")
    if not isinstance(value, dict):
        fail(f"{path.name} must contain a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate an IR-V3 blind-run bundle")
    parser.add_argument("--challenge", required=True, type=Path)
    parser.add_argument("--bundle", required=True, type=Path)
    args = parser.parse_args()

    challenge = args.challenge.read_bytes()
    challenge_doc = load_json(args.challenge)
    challenge_sha = sha256_bytes(challenge)

    if challenge_sha != EXPECTED_CHALLENGE_SHA256:
        fail("challenge SHA-256 does not match the frozen IR-V3 identity")
    if challenge_doc.get("challenge_id") != EXPECTED_CHALLENGE_ID:
        fail("challenge_id is not IR-V3")
    if challenge_doc.get("schema_version") != EXPECTED_SCHEMA_VERSION:
        fail("schema_version is not 3.0.0")

    bundle = args.bundle
    raw_path = bundle / "raw_result.bin"
    nonce_path = bundle / "nonce.private.txt"
    commitment_path = bundle / "commitment.json"
    provenance_path = bundle / "provenance.json"
    required = (raw_path, nonce_path, commitment_path, provenance_path)
    missing = [p.name for p in required if not p.is_file()]
    if missing:
        fail("missing required bundle files: " + ", ".join(missing))

    raw = raw_path.read_bytes()
    if not raw:
        fail("raw_result.bin is empty")
    nonce = nonce_path.read_text(encoding="utf-8")
    if not nonce or nonce != nonce.strip():
        fail("nonce.private.txt is empty or contains surrounding whitespace")

    commitment_doc = load_json(commitment_path)
    provenance = load_json(provenance_path)

    expected_raw_sha = sha256_bytes(raw)
    expected_commitment = commitment(raw, nonce)

    if commitment_doc.get("challenge_sha256") != challenge_sha:
        fail("commitment challenge_sha256 mismatch")
    if commitment_doc.get("submission_sha256") != expected_commitment:
        fail("submission commitment does not match raw result + nonce")
    if provenance.get("challenge_sha256") != challenge_sha:
        fail("provenance challenge_sha256 mismatch")
    if provenance.get("raw_result_sha256") != expected_raw_sha:
        fail("provenance raw_result_sha256 mismatch")
    if provenance.get("exit_code") != 0:
        fail("provenance exit_code is not zero")
    if provenance.get("epistemic_status") != EXPECTED_EPISTEMIC_STATUS + "; NOT_EXTERNAL_INDEPENDENCE_BY_ITSELF":
        fail("bundle is not explicitly classified as a raw blind run")
    if provenance.get("candidate_visibility", "").startswith("NOT_ASSERTED_BY_RUNNER") is False:
        fail("candidate visibility must remain separately adjudicated")

    print("IR_V3_BUNDLE=VALID")
    print("IR_V3_SEMANTIC_ADEQUACY=NOT_EVALUATED")
    print("IR_V3_MATERIAL_EXTERNAL_INDEPENDENCE=NOT_ESTABLISHED")
    print(f"challenge_sha256={challenge_sha}")
    print(f"raw_result_sha256={expected_raw_sha}")
    print(f"submission_commitment={expected_commitment}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
