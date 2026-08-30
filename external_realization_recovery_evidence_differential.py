"""Clean-room recovery/evidence differential experiment.

Question: can UNKNOWN, PARTIAL, DUPLICATE, STALE and REVOKED remain distinct
without conflating acknowledgement, external effect, and verification?

Generic evidence only; no Genesis ontology claim.
"""
from dataclasses import dataclass
from enum import Enum


class Recovery(Enum):
    UNKNOWN = "UNKNOWN"
    PARTIAL = "PARTIAL"
    DUPLICATE = "DUPLICATE"
    STALE = "STALE"
    REVOKED = "REVOKED"


@dataclass(frozen=True)
class Observation:
    accepted: bool
    revoked: bool
    effect_count: int
    acknowledgement: bool
    verified_effect: bool
    evidence_binding: str
    version_current: bool
    request_match: bool


def classify(o: Observation) -> Recovery:
    if o.revoked and not o.accepted:
        return Recovery.REVOKED
    if not o.version_current:
        return Recovery.STALE
    if not o.request_match:
        return Recovery.UNKNOWN
    if o.effect_count > 1:
        return Recovery.DUPLICATE
    if o.effect_count == 1 and not o.verified_effect:
        return Recovery.UNKNOWN
    if o.effect_count == 1 and o.verified_effect and o.evidence_binding == "partial":
        return Recovery.PARTIAL
    return Recovery.UNKNOWN


CASES = {
    "unknown_after_ack": Observation(True, False, 0, True, False, "none", True, True),
    "unknown_after_effect": Observation(True, False, 1, False, False, "bound", True, True),
    "partial": Observation(True, False, 1, True, True, "partial", True, True),
    "duplicate": Observation(True, False, 2, True, True, "bound", True, True),
    "stale": Observation(True, False, 1, True, True, "bound", False, True),
    "revoked": Observation(False, True, 0, False, False, "none", True, True),
}


def main():
    expected = {
        "unknown_after_ack": Recovery.UNKNOWN,
        "unknown_after_effect": Recovery.UNKNOWN,
        "partial": Recovery.PARTIAL,
        "duplicate": Recovery.DUPLICATE,
        "stale": Recovery.STALE,
        "revoked": Recovery.REVOKED,
    }
    for name, state in CASES.items():
        assert classify(state) == expected[name]

    # ACK does not establish effect or verification.
    ack_flip = Observation(**{**CASES["unknown_after_effect"].__dict__, "acknowledgement": True})
    assert classify(ack_flip) == Recovery.UNKNOWN
    ack_only = Observation(True, False, 1, True, False, "bound", True, True)
    assert classify(ack_only) == Recovery.UNKNOWN

    # Effect and evidence/verification remain separate from acknowledgement.
    partial_without_verification = Observation(True, False, 1, True, False, "partial", True, True)
    assert classify(partial_without_verification) == Recovery.UNKNOWN

    # Duplicate effect is not ordinary success.
    assert classify(CASES["duplicate"]) == Recovery.DUPLICATE

    # Request binding and freshness remain independent observations.
    assert classify(Observation(True, False, 1, True, True, "bound", True, False)) == Recovery.UNKNOWN
    assert classify(Observation(True, False, 1, True, True, "bound", False, True)) == Recovery.STALE

    # Revocation is not equivalent to failure or absence of effect.
    assert classify(CASES["revoked"]) == Recovery.REVOKED

    # Red team: contradictory evidence must not silently become verified.
    contradictory = Observation(True, False, 1, True, False, "contradictory", True, True)
    assert classify(contradictory) == Recovery.UNKNOWN

    print("recovery/evidence differential: PASS")
    print("cases=6")
    print("acknowledgement_distinct_from_effect=True")
    print("acknowledgement_distinct_from_verification=True")
    print("unknown_not_failed_or_safe_retry=True")
    print("contradictory_evidence_not_verified=True")
    print("canonical_ontology_claim=False")


if __name__ == "__main__":
    main()
