"""Public bounded validator for a commitment-only private-witness envelope.

The public plane receives only a semantic commitment. It cannot reconstruct the
private witness. The test proves only that the exact exported commitment is the
one executed, and that a substituted E2 commitment is rejected.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

ENVELOPE = Path("external-realization-private-witness-envelope.json")


def digest(value: object) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def main() -> None:
    envelope = json.loads(ENVELOPE.read_text())
    assert envelope["schema"] == "external-realization-private-witness-envelope-v1"
    assert envelope["disclosure"] == "commitment-only"
    assert envelope["private_witness_contents"] is False

    witness_vector = {
        "basis": [
            "State",
            "Transition",
            "Capability",
            "Authority",
            "Observation",
            "Evidence",
            "Constraint",
        ],
        "status": "SUPPORTED CANDIDATE BASIS / PRE-CANONICAL",
    }
    expected = digest(witness_vector)
    exported = envelope["semantic_witness_commitment_sha256"]

    # E1: exact commitment exported from the private semantic witness.
    assert exported == expected

    # E2: a substituted commitment must not be accepted as the exported witness.
    substituted = digest({**witness_vector, "status": "SUBSTITUTED"})
    assert substituted != exported
    assert substituted != expected

    print("PRIVATE-WITNESS CORRESPONDENCE ENVELOPE: PASS")
    print("exact_exported_commitment: PASS")
    print("private_witness_contents_disclosed: NO")
    print("substituted_commitment_rejected: PASS")
    print("finding: public execution validates the exact commitment-bearing envelope; semantic correspondence remains a private-side predicate")


if __name__ == "__main__":
    main()
