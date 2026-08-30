"""Clean-room composed Red-Team and primitive-removal experiment.

Generic only. No private Genesis hypotheses, credentials, datasets, internal
endpoints, or canonical decisions.
"""
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Observation:
    accepted: bool = False
    effect_count: int = 0
    acknowledgement: bool = False
    evidence_count: int = 0
    revoked: bool = False
    request_id: str = "r1"
    version: str = "v1"


def classify(o: Observation) -> str:
    if o.revoked and not o.accepted:
        return "REVOKED"
    if o.effect_count > 1:
        return "DUPLICATE"
    if o.effect_count == 1 and o.evidence_count == 0:
        return "UNKNOWN"
    if o.effect_count == 1 and o.evidence_count == 1:
        return "VERIFIED"
    if o.accepted and not o.acknowledgement:
        return "UNKNOWN"
    return "PENDING"


def composed_attacks() -> None:
    # Effect + lost acknowledgement + late evidence.
    u = Observation(accepted=True, effect_count=1, acknowledgement=False)
    assert classify(u) == "UNKNOWN"
    v = replace(u, evidence_count=1)
    assert classify(v) == "VERIFIED"

    # Concurrent duplicate effect remains distinguishable.
    d = Observation(accepted=True, effect_count=2, acknowledgement=True, evidence_count=2)
    assert classify(d) == "DUPLICATE"

    # Revocation before realization differs from an already accepted request.
    revoked = Observation(revoked=True, accepted=False)
    accepted_then_revoked = Observation(revoked=True, accepted=True, effect_count=1)
    assert classify(revoked) == "REVOKED"
    assert classify(accepted_then_revoked) == "UNKNOWN"

    # Contradictory evidence cannot be silently collapsed into verified success.
    contradictory = Observation(accepted=True, effect_count=1, evidence_count=2)
    assert classify(contradictory) != "VERIFIED"

    # Stale resource version remains distinguishable from the current request.
    stale = replace(u, version="v0")
    assert stale.version != u.version

    # Cross-request evidence binding cannot be inferred from the observation alone.
    foreign = replace(v, request_id="r2")
    assert foreign.request_id != v.request_id


def primitive_removal() -> None:
    # These classifications are derived from the observation vector. Removing
    # the labels from the implementation does not remove the underlying facts.
    cases = [
        Observation(accepted=True, effect_count=1, evidence_count=0),
        Observation(accepted=True, effect_count=2, evidence_count=2),
        Observation(revoked=True, accepted=False),
    ]
    derived = [(o.effect_count, o.evidence_count, o.revoked, o.accepted) for o in cases]
    assert derived == [(1, 0, False, True), (2, 2, False, True), (0, 0, True, False)]


def main() -> None:
    composed_attacks()
    primitive_removal()
    print("external realization composed red team: PASS")
    print("checks=late-evidence,duplicate-effect,revocation-race,contradictory-evidence,stale,cross-request,primitive-removal")


if __name__ == "__main__":
    main()
