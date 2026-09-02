#!/usr/bin/env python3
"""Small deterministic regression suite for the public BFV-1 verifier."""
from __future__ import annotations

import hashlib
import json
import tempfile
from pathlib import Path

from verify_submission import verify


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, separators=(",", ":")) + "\n", encoding="utf-8")


def main() -> int:
    corpus = {
        "protocol_version": "BFV-1",
        "corpus_id": "selftest",
        "obligations": [
            {"obligation_id": "O001", "text": "A condition changes after an operation."},
            {"obligation_id": "O002", "text": "A permission can be withdrawn."},
        ],
    }
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        corpus_path = root / "corpus.json"
        valid_path = root / "valid.json"
        invalid_path = root / "invalid.json"
        write_json(corpus_path, corpus)
        digest = hashlib.sha256(corpus_path.read_bytes()).hexdigest()
        valid = {
            "protocol_version": "BFV-1",
            "corpus_sha256": digest,
            "factors": [{"factor_id": "F001"}, {"factor_id": "F002"}],
            "coverage": [
                {"obligation_id": "O001", "factor_ids": ["F001"]},
                {"obligation_id": "O002", "factor_ids": ["F002"]},
            ],
        }
        invalid = dict(valid)
        invalid["coverage"] = [{"obligation_id": "O001", "factor_ids": ["F001"]}]
        write_json(valid_path, valid)
        write_json(invalid_path, invalid)
        assert verify(corpus_path, valid_path) == 0
        assert verify(corpus_path, invalid_path) == 1
    print("PASS: BFV-1 verifier self-test")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
