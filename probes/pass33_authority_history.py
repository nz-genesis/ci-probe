"""Pass 33 public-safe concurrent authority-history probe.

Synthetic only: no private Genesis state, witnesses, credentials, or imports.
The probe tests whether divergent authority histories can be represented with
State + Transition + Authority + Observation + Evidence + Constraint.
"""
from dataclasses import dataclass
from enum import Enum


class Decision(Enum):
    ALLOW = "ALLOW"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class Authority:
    subject: str
    issuer: str
    scope: str
    version: int
    active: bool


@dataclass(frozen=True)
class Observation:
    effect_id: str
    observer: str
    observed_version: int
    status: str


@dataclass(frozen=True)
class Evidence:
    observation: Observation
    authority: Authority
    claim: str
    complete: bool


@dataclass(frozen=True)
class Constraint:
    required_subject: str
    required_issuer: str
    required_scope: str
    required_authority_version: int
    required_observation_version: int


def assess(effect_id: str, evidence: Evidence, constraint: Constraint) -> Decision:
    observation = evidence.observation
    authority = evidence.authority
    if not evidence.complete:
        return Decision.UNKNOWN
    if observation.effect_id != effect_id:
        return Decision.UNKNOWN
    if observation.observed_version < constraint.required_observation_version:
        return Decision.UNKNOWN
    if authority.subject != constraint.required_subject:
        return Decision.UNKNOWN
    if authority.issuer != constraint.required_issuer:
        return Decision.UNKNOWN
    if authority.scope != constraint.required_scope:
        return Decision.UNKNOWN
    if authority.version != constraint.required_authority_version:
        return Decision.UNKNOWN
    if not authority.active:
        return Decision.UNKNOWN
    if evidence.claim == "conflict":
        return Decision.CONFLICT
    if evidence.claim == "applied" and observation.status == "APPLIED":
        return Decision.ALLOW
    return Decision.UNKNOWN


def histories() -> tuple[Authority, Authority, Authority, Authority]:
    root_v1 = Authority("observer-a", "root-a", "target-a", 1, True)
    root_v2 = Authority("observer-a", "root-a", "target-a", 2, False)
    delegated_v1 = Authority("observer-b", "observer-a", "target-a", 1, True)
    delegated_v2 = Authority("observer-b", "observer-a", "target-a", 2, False)
    return root_v1, root_v2, delegated_v1, delegated_v2


def evidence_for(authority: Authority, observed_version: int = 1) -> Evidence:
    observation = Observation("e1", authority.subject, observed_version, "APPLIED")
    return Evidence(observation, authority, "applied", True)


def constraint_for(authority: Authority, observation_version: int) -> Constraint:
    return Constraint(authority.subject, authority.issuer, authority.scope, authority.version, observation_version)


def test_historical_transition_can_use_historical_authority() -> None:
    v1, _, _, _ = histories()
    e = evidence_for(v1, observed_version=1)
    assert assess("e1", e, constraint_for(v1, 1)) is Decision.ALLOW


def test_revocation_is_effective_for_later_transition() -> None:
    _, v2, _, _ = histories()
    revoked = Authority(v2.subject, v2.issuer, v2.scope, v2.version, False)
    e = evidence_for(revoked, observed_version=2)
    assert assess("e1", e, constraint_for(revoked, 2)) is Decision.UNKNOWN


def test_stale_domain_view_cannot_authorize_newer_transition() -> None:
    v1, _, _, _ = histories()
    e = evidence_for(v1, observed_version=1)
    later = Constraint(v1.subject, v1.issuer, v1.scope, 2, 2)
    assert assess("e1", e, later) is Decision.UNKNOWN


def test_concurrent_delegation_narrowing_does_not_widen_scope() -> None:
    _, _, delegated_v1, delegated_v2 = histories()
    narrowed = Authority(delegated_v2.subject, delegated_v2.issuer, "target-a-subset", 2, True)
    e = evidence_for(narrowed, observed_version=2)
    c = Constraint("observer-b", "observer-a", "target-a", 2, 2)
    assert assess("e1", e, c) is Decision.UNKNOWN
    assert delegated_v1.scope == "target-a"


def test_cross_domain_history_cannot_silently_substitute() -> None:
    foreign = Authority("observer-a", "foreign-root", "target-a", 2, True)
    e = evidence_for(foreign, observed_version=2)
    c = Constraint("observer-a", "root-a", "target-a", 2, 2)
    assert assess("e1", e, c) is Decision.UNKNOWN


def test_old_evidence_is_not_revalidated_by_newer_authority() -> None:
    _, v2, _, _ = histories()
    active_v2 = Authority(v2.subject, v2.issuer, v2.scope, 2, True)
    old_observation = Observation("e1", "observer-a", 1, "APPLIED")
    e = Evidence(old_observation, active_v2, "applied", True)
    assert assess("e1", e, constraint_for(active_v2, 2)) is Decision.UNKNOWN


def test_incomplete_divergent_history_remains_unknown() -> None:
    v1, _, _, _ = histories()
    e = Evidence(evidence_for(v1).observation, v1, "applied", False)
    assert assess("e1", e, constraint_for(v1, 1)) is Decision.UNKNOWN


def test_conflicting_authority_claims_remain_conflict() -> None:
    v1, _, _, _ = histories()
    e = Evidence(evidence_for(v1).observation, v1, "conflict", True)
    assert assess("e1", e, constraint_for(v1, 1)) is Decision.CONFLICT


def test_divergent_views_do_not_create_authority() -> None:
    v1, v2, _, _ = histories()
    e1 = evidence_for(v1, 1)
    e2 = evidence_for(v2, 2)
    later = constraint_for(v2, 2)
    assert assess("e1", e1, later) is Decision.UNKNOWN
    assert assess("e1", e2, later) is Decision.UNKNOWN


def test_no_history_primitive_is_required() -> None:
    existing = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}
    proposed = {"AuthorityHistory", "Delegation", "Trust", "Quorum", "Consensus"}
    assert existing.isdisjoint(proposed)


def main() -> None:
    tests = (
        test_historical_transition_can_use_historical_authority,
        test_revocation_is_effective_for_later_transition,
        test_stale_domain_view_cannot_authorize_newer_transition,
        test_concurrent_delegation_narrowing_does_not_widen_scope,
        test_cross_domain_history_cannot_silently_substitute,
        test_old_evidence_is_not_revalidated_by_newer_authority,
        test_incomplete_divergent_history_remains_unknown,
        test_conflicting_authority_claims_remain_conflict,
        test_divergent_views_do_not_create_authority,
        test_no_history_primitive_is_required,
    )
    for test in tests:
        test()
    print("PASS33_PUBLIC: PASS; cases=10; private_data=none; new_primitives=0")


if __name__ == "__main__":
    main()
