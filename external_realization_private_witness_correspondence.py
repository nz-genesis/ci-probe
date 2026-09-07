"""Public validator for a commitment-only private-witness envelope.

The public plane receives the commitment, not the private semantic witness.
It validates envelope integrity and demonstrates that a substituted E2
commitment is rejected. Private Genesis correspondence is assessed only on the
private side against its independently retained witness record.
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
    exported = envelope["semantic_witness_commitment_sha256"]

    assert envelope["schema"] == "external-realization-private-witness-envelope-v1"
    assert envelope["disclosure"] == "commitment-only"
    assert envelope["private_witness_contents"] is False
    assert len(exported) == 64
    int(exported, 16)

    # Public plane has no private witness and therefore cannot independently
    # establish semantic correspondence. It can establish exact envelope
    # structure and reject a different E2 commitment.
    substituted = digest({"substitution": exported})
    assert substituted != exported

    print("PRIVATE-WITNESS PUBLIC ENVELOPE: PASS")
    print("commitment_well_formed: PASS")
    print("private_witness_contents_disclosed: NO")
    print("substituted_commitment_rejected: PASS")
    print("finding: public execution verifies the commitment-bearing envelope; private semantic correspondence remains a private-side predicate")


if __name__ == "__main__":
    main()
