#!/usr/bin/env python3
"""Verify that the public independent-replication surface has one active challenge.

This is a structural consistency check only. It does not adjudicate semantic
correctness or material independence.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CHALLENGE = ROOT / "challenge-v3.json"
MANIFEST = ROOT / "ACTIVE_MANIFEST.md"
README = ROOT / "README.md"
CALL = ROOT / "INDEPENDENT_REPLICATION_CALL.md"
RUNBOOK = ROOT / "EXTERNAL_PARTICIPANT_RUNBOOK_V2.md"
PROTOCOL = ROOT / "EXTERNAL_AGENT_EXECUTION_PROTOCOL_V2.md"

EXPECTED_ID = "IR-V3"
EXPECTED_SCHEMA = "3.0.0"
EXPECTED_SHA256 = "913c162ede3741ead44dca3efe3fbbf33f5de764254d6a2da88cc90cf08b05a"
EXPECTED_GIT_BLOB_SHA1 = "50f41fdc1a7d563367fb07316f2c84adc95c74a0"
EXPECTED_COMMIT = "3d37e023b49a995b466954445c1672f5d7ef046d"


def main() -> int:
    errors: list[str] = []

    if not CHALLENGE.is_file():
        errors.append("missing challenge-v3.json")
    else:
        challenge_bytes = CHALLENGE.read_bytes()
        actual_sha256 = hashlib.sha256(challenge_bytes).hexdigest()
        if actual_sha256 != EXPECTED_SHA256:
            errors.append(
                "challenge-v3.json content SHA-256 mismatch: "
                f"expected {EXPECTED_SHA256}, got {actual_sha256}"
            )
        try:
            challenge = json.loads(challenge_bytes.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            errors.append(f"challenge-v3.json is not valid UTF-8 JSON: {exc}")
        else:
            if challenge.get("challenge_id") != EXPECTED_ID:
                errors.append("challenge-v3.json has unexpected challenge_id")
            if challenge.get("schema_version") != EXPECTED_SCHEMA:
                errors.append("challenge-v3.json has unexpected schema_version")

    required_files = [MANIFEST, README, CALL, RUNBOOK, PROTOCOL]
    for path in required_files:
        if not path.is_file():
            errors.append(f"missing active-surface file: {path.name}")
            continue
        text = path.read_text(encoding="utf-8")
        for marker in (EXPECTED_ID, "challenge-v3.json", EXPECTED_SHA256):
            if marker not in text:
                errors.append(f"{path.name} missing active marker: {marker}")

    manifest = MANIFEST.read_text(encoding="utf-8") if MANIFEST.is_file() else ""
    if manifest and "**Status:** ACTIVE / IR-V3" not in manifest:
        errors.append("ACTIVE_MANIFEST.md does not declare ACTIVE / IR-V3")
    if manifest and EXPECTED_COMMIT not in manifest:
        errors.append("ACTIVE_MANIFEST.md missing frozen IR-V3 commit")
    if manifest and EXPECTED_GIT_BLOB_SHA1 not in manifest:
        errors.append("ACTIVE_MANIFEST.md missing frozen-file Git blob SHA-1")
    if manifest and "challenge-v2.json` | historical frozen challenge | HISTORICAL / NOT ACTIVE" not in manifest:
        errors.append("ACTIVE_MANIFEST.md does not explicitly demote IR-V2 to historical status")

    active_docs = [MANIFEST, README, CALL, RUNBOOK, PROTOCOL]
    for path in active_docs:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if "ACTIVE / IR-V2" in text:
            errors.append(f"stale active IR-V2 status remains in {path.name}")
        if "Use **IR-V2**" in text:
            errors.append(f"stale active IR-V2 instruction remains in {path.name}")

    print(f"Independent-replication active surface files checked: {len(required_files)}")
    print(f"Active challenge identity: {EXPECTED_ID} / schema {EXPECTED_SCHEMA}")
    if CHALLENGE.is_file():
        print(f"Active challenge SHA-256: {hashlib.sha256(CHALLENGE.read_bytes()).hexdigest()}")
    print(f"Frozen-file Git blob SHA-1: {EXPECTED_GIT_BLOB_SHA1}")
    print(f"Active challenge verification: {'PASS' if not errors else 'FAIL'}")
    if errors:
        for error in errors:
            print(f"- {error}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
