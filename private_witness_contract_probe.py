"""Generic public contract test for Genesis private semantic witnesses.

This file intentionally contains only synthetic public fixtures. It verifies the
NON-DISCLOSING OUTPUT CONTRACT used by a private Genesis witness boundary. A
PASS here is not private Genesis evidence and must never be reported as such.
"""
from __future__ import annotations

import json

FORBIDDEN = {
    "private_note", "private_state", "secret", "token", "raw_state", "raw_private"
}
REQUIRED = {
    "format", "state_digest", "public_envelope_digest", "predicate_id",
    "semantic_result", "independent_witness_digest", "disclosure"
}


def validate(record: dict) -> None:
    assert set(record) == REQUIRED
    assert record["format"] == "genesis-private-semantic-witness/v1"
    assert isinstance(record["state_digest"], str) and record["state_digest"]
    assert isinstance(record["public_envelope_digest"], str) and record["public_envelope_digest"]
    assert isinstance(record["predicate_id"], str) and record["predicate_id"]
    assert isinstance(record["semantic_result"], bool)
    assert isinstance(record["independent_witness_digest"], str) and record["independent_witness_digest"]
    assert record["disclosure"] == "non-disclosing"
    assert not FORBIDDEN.intersection(record)


def main() -> None:
    synthetic_public_record = {
        "format": "genesis-private-semantic-witness/v1",
        "state_digest": "a" * 64,
        "public_envelope_digest": "b" * 64,
        "predicate_id": "synthetic.contract.valid",
        "semantic_result": True,
        "independent_witness_digest": "c" * 64,
        "disclosure": "non-disclosing",
    }
    validate(synthetic_public_record)

    leaked = dict(synthetic_public_record)
    leaked["private_state"] = {"should": "never appear"}
    try:
        validate(leaked)
    except AssertionError:
        pass
    else:
        raise AssertionError("private-field leakage was not rejected")

    print("PRIVATE WITNESS PUBLIC CONTRACT: 2/2 PASS")
    print("Interpretation: contract-only; no private Genesis evidence")


if __name__ == "__main__":
    main()
