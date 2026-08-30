"""Clean-room recovery/evidence differential experiment.

Question: can FAILED, UNKNOWN, PARTIAL, DUPLICATE, STALE and REVOKED remain
semantically distinct without conflating acknowledgement, external effect,
and verification?

Generic evidence only; no Genesis ontology claim.
"""
from dataclasses import dataclass
from enum import Enum


class Recovery(Enum):
    FAILED = "FAILED"
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
    expected_effect_count: int
    acknowledgement: bool
    verified_effect: bool
    evidence_bound: bool
    version_current: bool
    request_match: bool
    failure_established: bool


def classify(o: Observation) -> Recovery:
    if o.revoked and not o.accepted:
        return Recovery.REVOKED
    if not o.version_current:
        return Recovery.STALE
    if not o.request_match:
        return Recovery.UNKNOWN
    if o.effect_count > o.expected_effect_count:
        return Recovery.DUPLICATE
    if o.effect_count < o.expected_effect_count and o.effect_count > 0:
        return Recovery.PARTIAL
    if o.failure_established and o.effect_count == 0:
        return Recovery.FAILED
    if o.effect_count == 0:
        return Recovery.UNKNOWN
    if not o.verified_effect or not o.evidence_bound:
        return Recovery.UNKNOWN
    return Recovery.UNKNOWN


CASES = {
    "failed": Observation(False, False, 0, 1, False, False, True, True, True, True),
    "unknown_after_ack": Observation(True, False, 0, 1, True, False, False, True, True, False),
    "unknown_after_effect": Observation(True, False, 1, 1, False, False, True, True, True, False),
    "partial": Observation(True, False, 1, 2, True, True, True, True, True, False),
    "duplicate": Observation(True, False, 2, 1, True, True, True, True, True, False),
    "stale": Observation(True, False, 1, 1, True, True, True, False, True, False),
    "revoked": Observation(False, True, 0, 1, False, False, False, True, True, False),
}


def retry_disposition(o: Observation) -> str:
    """A bounded safety policy, not an ontology claim."""
    result = classify(o)
    if result == Recovery.FAILED:
        return "ALLOW_ONLY_IF_EXTERNAL_CONTRACT_PERMITS"
    return "BLOCK_UNTIL_NEW_EVIDENCE"


def main():
    expected = {
        "failed": Recovery.FAILED,
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
    ack_only = Observation(True, False, 1, 1, True, False, True, True, True, False)
    assert classify(ack_only) == Recovery.UNKNOWN

    # Effect, verification and provenance binding remain separate observations.
    no_binding = Observation(True, False, 1, 1, True, True, False, True, True, False)
    assert classify(no_binding) == Recovery.UNKNOWN
    no_verification = Observation(True, False, 1, 1, True, False, True, True, True, False)
    assert classify(no_verification) == Recovery.UNKNOWN

    # Partial is derived from an independent count mismatch, not a semantic label.
    assert classify(Observation(True, False, 1, 2, True, True, True, True, True, False)) == Recovery.PARTIAL

    # Duplicate effect is derived from effect_count > expected_effect_count.
    assert classify(Observation(True, False, 2, 1, True, True, True, True, True, False)) == Recovery.DUPLICATE

    # Established failure is distinct from UNKNOWN: absence of effect alone is insufficient.
    assert classify(Observation(True, False, 0, 1, False, False, True, True, True, False)) == Recovery.UNKNOWN
    assert classify(Observation(False, False, 0, 1, False, False, True, True, True, True)) == Recovery.FAILED

    # Request binding and freshness remain independent observations.
    assert classify(Observation(True, False, 1, 1, True, True, True, True, False, False)) == Recovery.UNKNOWN
    assert classify(Observation(True, False, 1, 1, True, True, True, False, True, False)) == Recovery.STALE

    # Revocation is not equivalent to failure or absence of effect.
    assert classify(CASES["revoked"]) == Recovery.REVOKED

    # Red team: contradictory/missing evidence must not silently become verified.
    contradictory = Observation(True, False, 1, 1, True, False, True, True, True, False)
    assert classify(contradictory) == Recovery.UNKNOWN

    # Red team: changing acknowledgement alone cannot change the classification.
    for state in CASES.values():
        flipped = Observation(**{**state.__dict__, "acknowledgement": not state.acknowledgement})
        assert classify(flipped) == classify(state)

    # UNKNOWN is not treated as retry-safe by this bounded policy.
    assert retry_disposition(CASES["unknown_after_ack"]) == "BLOCK_UNTIL_NEW_EVIDENCE"
    assert retry_disposition(CASES["unknown_after_effect"]) == "BLOCK_UNTIL_NEW_EVIDENCE"
    # Even established failure does not imply unconditional retry: an external
    # contract may prohibit or constrain re-execution.
    assert retry_disposition(CASES["failed"]) == "ALLOW_ONLY_IF_EXTERNAL_CONTRACT_PERMITS"

    print("recovery/evidence differential: PASS")
    print("cases=7")
    print("acknowledgement_distinct_from_effect=True")
    print("acknowledgement_distinct_from_verification=True")
    print("partial_derived_from_count_mismatch=True")
    print("duplicate_derived_from_effect_count=True")
    print("established_failure_distinct_from_unknown=True")
    print("unknown_not_failed_or_retry_safe=True")
    print("contradictory_evidence_not_verified=True")
    print("canonical_ontology_claim=False")


if __name__ == "__main__":
    main()
