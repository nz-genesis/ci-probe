#!/usr/bin/env python3
"""Fail-closed public validator for the P207 export boundary.

This validator intentionally knows nothing about private Genesis state or
private semantic authority. A successful result is public-contract evidence
only; it is not a private-to-public correspondence proof.
"""

from __future__ import annotations

import json
from pathlib import Path
import re
import sys

PATH = Path("probes/p207/private-witness-public-realization.json")
REQUIRED = {
    "format",
    "predicate_id",
    "realization_class",
    "disclosure",
}
ALLOWED = REQUIRED
FORMAT = "genesis-private-witness-public-realization/v1"
MAX_PREDICATE = 200
PRIVATE_MARKERS = (
    "private_state",
    "private-state",
    "private_corpus",
    "private-corpus",
    "semantic_authority_payload",
    "secret",
    "token",
    "password",
    "credential",
)


def fail(message: str) -> None:
    print(f"P207_PUBLIC_CONTRACT_FAIL: {message}")
    raise SystemExit(1)


def main() -> None:
    if not PATH.is_file():
        fail(f"missing export: {PATH}")

    try:
        data = json.loads(PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        fail(f"invalid JSON: {exc}")

    if not isinstance(data, dict):
        fail("top-level value must be an object")
    if set(data) != ALLOWED:
        fail(f"keys must be exactly {sorted(ALLOWED)}")
    if data["format"] != FORMAT:
        fail("unsupported format")
    if not isinstance(data["predicate_id"], str) or not data["predicate_id"]:
        fail("predicate_id must be a non-empty string")
    if len(data["predicate_id"]) > MAX_PREDICATE:
        fail("predicate_id too long")
    if not re.fullmatch(r"[A-Za-z0-9_.:-]+", data["predicate_id"]):
        fail("predicate_id contains unsupported characters")
    if data["realization_class"] != "public-contract-only":
        fail("realization_class must be public-contract-only")
    if data["disclosure"] != "non-disclosing":
        fail("disclosure must be non-disclosing")

    serialized = json.dumps(data, ensure_ascii=False).lower()
    for marker in PRIVATE_MARKERS:
        if marker in serialized:
            fail(f"private-content marker detected: {marker}")

    print("P207_PUBLIC_CONTRACT_PASS")
    print("scope=public-envelope-shape-and-non-disclosure-only")


if __name__ == "__main__":
    main()
