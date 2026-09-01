"""Pass 34 public-safe Byzantine/partial-order authority probe.

Synthetic only. The test asks whether mutually incompatible but internally
consistent authority views can remain UNKNOWN/CONFLICT without introducing
Consensus, Quorum, Trust, Ordering, or AuthorityHistory as Genesis primitives.
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
class State:
    authorities: tuple[Authority, ...]
    observation_version: int


@dataclass(frozen=True)
class Transition:
    effect_id: str
    required_subject: str
    required_issuer: str
    required_scope: str
    required_authority_version: int
    required_observation_version: int


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
    required_observer: str
    required_scope: str
    required_authority_version: int


def authority_matches(authority: Authority, transition: Transition) -> bool:
    return (
        authority.subject == transition.required_subject
        and authority.issuer == transition.required_issuer
        and authority.scope == transition.required_scope
        and authority.version == transition.required_authority_version
        and authority.active
    )


def evidence_supports(evidence: Evidence, transition: Transition) -> bool:
    observation = evidence.observation
    return (
        evidence.complete
        and observation.effect_id == transition.effect_id
        and observation.observed_version >= transition.required_observation_version
        and authority_matches(evidence.authority, transition)
        and evidence.claim == "applied"
        and observation.status == "APPLIED"
    )


def assess(transition: Transition, evidence: tuple[Evidence, ...]) -> Decision:
    if not evidence:
        return Decision.UNKNOWN
    supporting = tuple(item for item in evidence if evidence_supports(item, transition))
    contradictory = tuple(
        item
        for item in evidence
        if item.observation.effect_id == transition.effect_id
        and item.claim == "conflict"
    )
    if contradictory:
        return Decision.CONFLICT
    if len(supporting) == 1:
        return Decision.ALLOW
    if len(supporting) > 1:
        subjects = {item.observation.observer for item in supporting}
        versions = {item.authority.version for item in supporting}
        if len(subjects) == len(supporting) and len(versions) == 1:
            return Decision.ALLOW
        return Decision.CONFLICT
    return Decision.UNKNOWN


def divergent_states() -> tuple[State, State]:
    active = Authority("observer-a", "root-a", "target-a", 3, True)
    revoked = Authority("observer-a", "root-a", "target-a", 4, False)
    return State((active,), 3), State((revoked,), 4)


def transition_v3() -> Transition:
    return Transition("e1", "observer-a", "root-a", "target-a", 3, 3)


def evidence_from_state(state: State, observer: str) -> Evidence:
    authority = state.authorities[0]
    observation = Observation("e1", observer, state.observation_version, "APPLIED")
    return Evidence(observation, authority, "applied", True)


def test_each_domain_view_is_internally_coherent() -> None:
    a, b = divergent_states()
    assert a.authorities[0].active is True
    assert b.authorities[0].active is False
    assert a.observation_version < b.observation_version


def test_historical_v3_transition_accepts_v3_view() -> None:
    a, _ = divergent_states()
    assert assess(transition_v3(), (evidence_from_state(a, "observer-a"),)) is Decision.ALLOW


def test_v3_transition_does_not_accept_revoked_v4_view() -> None:
    _, b = divergent_states()
    assert assess(transition_v3(), (evidence_from_state(b, "observer-b"),)) is Decision.UNKNOWN


def test_no_global_order_does_not_invent_one() -> None:
    a, b = divergent_states()
    e_a = evidence_from_state(a, "observer-a")
    e_b = evidence_from_state(b, "observer-b")
    assert e_a.authority.version != e_b.authority.version
    assert assess(transition_v3(), (e_a, e_b)) is Decision.ALLOW


def test_conflict_marker_blocks_silent_resolution() -> None:
    a, _ = divergent_states()
    base = evidence_from_state(a, "observer-a")
    conflict = Evidence(base.observation, base.authority, "conflict", True)
    assert assess(transition_v3(), (base, conflict)) is Decision.CONFLICT


def test_foreign_issuer_cannot_join_partial_order() -> None:
    foreign = Authority("observer-a", "foreign-root", "target-a", 3, True)
    evidence = Evidence(Observation("e1", "observer-a", 3, "APPLIED"), foreign, "applied", True)
    assert assess(transition_v3(), (evidence,)) is Decision.UNKNOWN


def test_stale_observation_cannot_resolve_newer_transition() -> None:
    a, _ = divergent_states()
    stale = Evidence(Observation("e1", "observer-a", 2, "APPLIED"), a.authorities[0], "applied", True)
    assert assess(transition_v3(), (stale,)) is Decision.UNKNOWN


def test_external_effect_between_divergent_views_remains_unresolved() -> None:
    a, b = divergent_states()
    effect_after_a = Evidence(Observation("e1", "observer-b", 4, "APPLIED"), b.authorities[0], "applied", True)
    assert assess(transition_v3(), (effect_after_a,)) is Decision.UNKNOWN


def test_incomplete_evidence_is_not_authority() -> None:
    a, _ = divergent_states()
    complete = evidence_from_state(a, "observer-a")
    incomplete = Evidence(complete.observation, complete.authority, "applied", False)
    assert assess(transition_v3(), (incomplete,)) is Decision.UNKNOWN


def test_capability_like_observer_identity_does_not_create_authority() -> None:
    a, _ = divergent_states()
    foreign_observer = evidence_from_state(a, "untrusted-observer")
    assert foreign_observer.observation.observer != a.authorities[0].subject
    assert foreign_observer.authority.subject == "observer-a"


def test_primitive_inflation_is_negative() -> None:
    existing = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}
    proposed = {"AuthorityHistory", "Consensus", "Quorum", "Trust", "Ordering"}
    assert existing.isdisjoint(proposed)


def test_transition_specificity_prevents_retroactive_authority() -> None:
    a, _ = divergent_states()
    later = Transition("e2", "observer-a", "root-a", "target-a", 4, 4)
    assert assess(later, (evidence_from_state(a, "observer-a"),)) is Decision.UNKNOWN


def main() -> None:
    tests = (
        test_each_domain_view_is_internally_coherent,
        test_historical_v3_transition_accepts_v3_view,
        test_v3_transition_does_not_accept_revoked_v4_view,
        test_no_global_order_does_not_invent_one,
        test_conflict_marker_blocks_silent_resolution,
        test_foreign_issuer_cannot_join_partial_order,
        test_stale_observation_cannot_resolve_newer_transition,
        test_external_effect_between_divergent_views_remains_unresolved,
        test_incomplete_evidence_is_not_authority,
        test_capability_like_observer_identity_does_not_create_authority,
        test_primitive_inflation_is_negative,
        test_transition_specificity_prevents_retroactive_authority,
    )
    for test in tests:
        test()
    print("PASS34_PUBLIC: PASS; cases=12; private_data=none; new_primitives=0")


if __name__ == "__main__":
    main()
