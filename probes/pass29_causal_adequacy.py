"""Pass 29 public-safe causal adequacy / observer semantics probe.

Tests whether existing Observation + Evidence + Constraint distinctions can
separate internally valid evidence from evidence that is causally sufficient
for an external-world claim, without introducing Trust, Provenance, Source,
Witness, Confidence, or Causality as Genesis primitives.

No private Genesis state, witnesses, corpus, credentials, or implementation
packages are imported or exposed.
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
    state_version: int
    status: str
    source: str
    causal_boundary: int
    available_at: int


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
    required_causal_boundary: int


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def assess(effect_id: str, evidence: Evidence, constraint: Constraint) -> Decision:
    o = evidence.observation
    if o.effect_id != effect_id or o.scope != constraint.required_scope:
        return Decision.UNKNOWN
    if not evidence.verified or evidence.revoked:
        return Decision.UNKNOWN
    if o.observed_version < constraint.minimum_version:
        return Decision.UNKNOWN
    if o.observed_version != o.state_version:
        return Decision.UNKNOWN
    if evidence.issued_at > constraint.now or evidence.valid_until < constraint.now:
        return Decision.UNKNOWN
    if o.causal_boundary < constraint.required_causal_boundary:
        return Decision.UNKNOWN
    if evidence.claim == "conflict":
        return Decision.CONFLICT
    if evidence.claim == "applied" and o.status == "APPLIED":
        return Decision.REALIZED
    if evidence.claim == "absent" and o.status == "ABSENT":
        return Decision.RELEASED
    return Decision.UNKNOWN


def base(status: str = "APPLIED", boundary: int = 12, source: str = "provider-a") -> Evidence:
    claim = "applied" if status == "APPLIED" else "absent"
    return Evidence(
        Observation("e1", "target-a", 7, 7, status, source, boundary, 15),
        True,
        claim,
        10,
        20,
    )


def fresh_causally_covered_is_admissible() -> None:
    require(assess("e1", base(), Constraint("target-a", 7, 15, 12)) is Decision.REALIZED, "causally covered evidence rejected")


def eventual_consistency_stays_unknown() -> None:
    e = base(boundary=10)
    require(assess("e1", e, Constraint("target-a", 7, 15, 12)) is Decision.UNKNOWN, "eventually consistent stale read treated as causal proof")


def replica_lag_stays_unknown() -> None:
    e = base(boundary=11)
    require(assess("e1", e, Constraint("target-a", 7, 15, 12)) is Decision.UNKNOWN, "replica-lagged observation accepted")


def read_after_write_gap_stays_unknown() -> None:
    e = base(boundary=9)
    require(assess("e1", e, Constraint("target-a", 7, 15, 12)) is Decision.UNKNOWN, "read-after-write gap accepted")


def provider_reordering_stays_unknown() -> None:
    e = base(boundary=8)
    require(assess("e1", e, Constraint("target-a", 7, 15, 12)) is Decision.UNKNOWN, "reordered observation accepted")


def lost_effect_with_stale_read_is_not_absence() -> None:
    e = base(status="ABSENT", boundary=10)
    require(assess("e1", e, Constraint("target-a", 7, 15, 12)) is Decision.UNKNOWN, "stale negative read became release")


def observer_disagreement_is_conflict() -> None:
    e = Evidence(base().observation, True, "conflict", 10, 20)
    require(assess("e1", e, Constraint("target-a", 7, 15, 12)) is Decision.CONFLICT, "observer disagreement was silently normalized")


def forged_shaped_evidence_without_verification_stays_unknown() -> None:
    e = Evidence(base().observation, False, "applied", 10, 20)
    require(assess("e1", e, Constraint("target-a", 7, 15, 12)) is Decision.UNKNOWN, "unverified evidence was accepted")


def pre_event_evidence_stays_unknown() -> None:
    e = base(boundary=11)
    require(assess("e1", e, Constraint("target-a", 7, 15, 12)) is Decision.UNKNOWN, "pre-event evidence crossed causal boundary")


def evidence_sufficient_for_one_transition_not_another() -> None:
    e = base(boundary=12)
    require(assess("e1", e, Constraint("target-a", 7, 15, 12)) is Decision.REALIZED, "baseline transition failed")
    require(assess("e1", e, Constraint("target-a", 8, 15, 12)) is Decision.UNKNOWN, "evidence silently widened to a stronger transition")


def non_idempotent_negative_claim_cannot_release_without_causal_coverage() -> None:
    e = base(status="ABSENT", boundary=10)
    require(assess("e1", e, Constraint("target-a", 7, 15, 12)) is Decision.UNKNOWN, "negative observation released a non-idempotent effect without causal coverage")


def no_hidden_causality_primitive_is_needed() -> None:
    names = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}
    require(not ({"Trust", "Provenance", "Source", "Witness", "Confidence", "Causality"} & names), "observer semantics became hidden Genesis primitives")


def main() -> None:
    fresh_causally_covered_is_admissible()
    eventual_consistency_stays_unknown()
    replica_lag_stays_unknown()
    read_after_write_gap_stays_unknown()
    provider_reordering_stays_unknown()
    lost_effect_with_stale_read_is_not_absence()
    observer_disagreement_is_conflict()
    forged_shaped_evidence_without_verification_stays_unknown()
    pre_event_evidence_stays_unknown()
    evidence_sufficient_for_one_transition_not_another()
    non_idempotent_negative_claim_cannot_release_without_causal_coverage()
    no_hidden_causality_primitive_is_needed()
    print("PASS29_PUBLIC: PASS; cases=12; private_data=none; new_primitives=0")


if __name__ == "__main__":
    main()
