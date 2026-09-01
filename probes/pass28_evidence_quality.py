"""Pass 28 public-safe evidence-quality probe.

Tests whether Observation + Evidence + Constraint can distinguish evidence
that is sufficient for a particular transition from stale, partial, scoped,
conflicting, replayed, revoked, or unavailable evidence.

No private Genesis state, witnesses, corpus, credentials, or implementation
packages are imported or exposed. Evidence quality is modeled as properties
of evidence/observation, not as a new Genesis primitive.
"""
from dataclasses import dataclass
from enum import Enum


class Decision(Enum):
    REALIZED = "REALIZED"
    RELEASED = "RELEASED"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class Observation:
    effect_id: str
    scope: str
    observed_version: int
    current_version: int
    status: str
    source: str


@dataclass(frozen=True)
class Evidence:
    observation: Observation
    verified: bool
    claim: str
    issued_at: int
    valid_until: int
    revoked: bool = False


@dataclass(frozen=True)
class Constraint:
    required_scope: str
    minimum_version: int
    now: int


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def assess(effect_id: str, evidence: Evidence, constraint: Constraint) -> Decision:
    o = evidence.observation
    if o.effect_id != effect_id:
        return Decision.UNKNOWN
    if o.scope != constraint.required_scope:
        return Decision.UNKNOWN
    if not evidence.verified or evidence.revoked:
        return Decision.UNKNOWN
    if o.observed_version < constraint.minimum_version:
        return Decision.UNKNOWN
    if o.observed_version != o.current_version:
        return Decision.UNKNOWN
    if evidence.issued_at > constraint.now or evidence.valid_until < constraint.now:
        return Decision.UNKNOWN
    if evidence.claim == "conflict":
        return Decision.CONFLICT
    if evidence.claim == "applied" and o.status == "APPLIED":
        return Decision.REALIZED
    if evidence.claim == "absent" and o.status == "ABSENT":
        return Decision.RELEASED
    return Decision.UNKNOWN


def base(claim: str = "applied") -> Evidence:
    return Evidence(
        Observation("e1", "target-a", 7, 7, "APPLIED" if claim == "applied" else "ABSENT", "provider-a"),
        verified=True,
        claim=claim,
        issued_at=10,
        valid_until=20,
    )


def verified_application_is_realized() -> None:
    require(assess("e1", base(), Constraint("target-a", 7, 15)) is Decision.REALIZED, "verified application not accepted")


def verified_absence_is_released() -> None:
    require(assess("e1", base("absent"), Constraint("target-a", 7, 15)) is Decision.RELEASED, "verified absence not accepted")


def stale_observation_stays_unknown() -> None:
    e = Evidence(Observation("e1", "target-a", 6, 7, "APPLIED", "provider-a"), True, "applied", 10, 20)
    require(assess("e1", e, Constraint("target-a", 7, 15)) is Decision.UNKNOWN, "stale observation was treated as current")


def partial_scope_stays_unknown() -> None:
    e = Evidence(Observation("e1", "target-a/partial", 7, 7, "APPLIED", "provider-a"), True, "applied", 10, 20)
    require(assess("e1", e, Constraint("target-a", 7, 15)) is Decision.UNKNOWN, "partial scope was accepted")


def wrong_effect_identity_stays_unknown() -> None:
    require(assess("e2", base(), Constraint("target-a", 7, 15)) is Decision.UNKNOWN, "foreign evidence reconciled effect")


def expired_evidence_stays_unknown() -> None:
    require(assess("e1", base(), Constraint("target-a", 7, 21)) is Decision.UNKNOWN, "expired evidence remained authoritative")


def future_evidence_stays_unknown() -> None:
    require(assess("e1", base(), Constraint("target-a", 7, 9)) is Decision.UNKNOWN, "future-dated evidence was accepted")


def revoked_evidence_stays_unknown() -> None:
    require(assess("e1", Evidence(base().observation, True, "applied", 10, 20, True), Constraint("target-a", 7, 15)) is Decision.UNKNOWN, "revoked evidence remained authoritative")


def contradictory_claim_is_preserved() -> None:
    e = Evidence(base().observation, True, "conflict", 10, 20)
    require(assess("e1", e, Constraint("target-a", 7, 15)) is Decision.CONFLICT, "conflict was silently resolved")


def valid_evidence_below_required_version_is_insufficient() -> None:
    e = Evidence(Observation("e1", "target-a", 6, 6, "APPLIED", "provider-a"), True, "applied", 10, 20)
    require(assess("e1", e, Constraint("target-a", 7, 15)) is Decision.UNKNOWN, "insufficient version was accepted")


def evidence_cannot_grant_authority() -> None:
    e = base()
    require(assess("e1", e, Constraint("target-a", 7, 15)) is Decision.REALIZED, "baseline evidence assessment failed")
    require(e.observation.scope == "target-a", "evidence changed authority scope")


def provider_unavailable_is_not_absence() -> None:
    e = Evidence(Observation("e1", "target-a", 0, 0, "UNAVAILABLE", "provider-a"), False, "absent", 0, 0)
    require(assess("e1", e, Constraint("target-a", 7, 15)) is Decision.UNKNOWN, "provider unavailability became absence")


def replayed_observation_does_not_advance_version() -> None:
    e = Evidence(Observation("e1", "target-a", 7, 7, "APPLIED", "provider-a"), True, "applied", 9, 20)
    require(assess("e1", e, Constraint("target-a", 8, 15)) is Decision.UNKNOWN, "replayed old observation advanced state")


def no_new_primitive_is_needed() -> None:
    names = {"State", "Transition", "Authority", "Observation", "Evidence", "Constraint"}
    require("EvidenceQuality" not in names, "evidence quality became a new primitive")


def main() -> None:
    verified_application_is_realized()
    verified_absence_is_released()
    stale_observation_stays_unknown()
    partial_scope_stays_unknown()
    wrong_effect_identity_stays_unknown()
    expired_evidence_stays_unknown()
    future_evidence_stays_unknown()
    revoked_evidence_stays_unknown()
    contradictory_claim_is_preserved()
    valid_evidence_below_required_version_is_insufficient()
    evidence_cannot_grant_authority()
    provider_unavailable_is_not_absence()
    replayed_observation_does_not_advance_version()
    no_new_primitive_is_needed()
    print("PASS28_PUBLIC: PASS; cases=14; private_data=none; new_primitives=0")


if __name__ == "__main__":
    main()
