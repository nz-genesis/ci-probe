#!/usr/bin/env python3
"""Mutation tests for the P207 public boundary validator."""

from __future__ import annotations

import json
from pathlib import Path
import tempfile

import p207_public_witness_contract as validator

BASE = {
    "format": "genesis-private-witness-public-realization/v1",
    "predicate_id": "synapse.admission_boundary.exists_and_is_verified",
    "realization_class": "public-contract-only",
    "disclosure": "non-disclosing",
}

CASES = {
    "unexpected-key": {**BASE, "extra": "must-fail"},
    "wrong-disclosure": {**BASE, "disclosure": "disclosing"},
    "wrong-realization-class": {**BASE, "realization_class": "private-runtime"},
    "private-field": {**BASE, "private_state": "must-not-cross-boundary"},
    "bad-predicate": {**BASE, "predicate_id": "bad predicate"},
}


def expect_failure(name: str, payload: dict, directory: Path) -> None:
    path = directory / f"{name}.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    validator.PATH = path
    try:
        validator.main()
    except SystemExit as exc:
        if exc.code == 1:
            print(f"RED_TEAM_PASS: {name}")
            return
        raise AssertionError(f"{name}: unexpected exit code {exc.code}")
    raise AssertionError(f"{name}: mutation was accepted")


def main() -> None:
    with tempfile.TemporaryDirectory() as raw:
        directory = Path(raw)
        for name, payload in CASES.items():
            expect_failure(name, payload, directory)
    print("P207_PUBLIC_CONTRACT_RED_TEAM_PASS")


if __name__ == "__main__":
    main()
