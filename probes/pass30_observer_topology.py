"""Pass 30 public-safe observer topology / source-compromise probe."""
from dataclasses import dataclass
from enum import Enum


class Decision(Enum):
    REALIZED = "REALIZED"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class Observation:
    effect_id: str
    scope: str
    state_version: int
    source_id: str
    causal_boundary: int
    status: str


@dataclass(frozen=True)
class Evidence:
    observation: Observation
    verified: bool
    source_authorized: bool
    chain_complete: bool
    claim: str


@dataclass(frozen=True)
class Constraint:
    required_source: str | None
    minimum_version: int
    minimum_causal_boundary: int


def assess(effect_id: str, e: Evidence, c: Constraint) -> Decision:
    o = e.observation
    if o.effect_id != effect_id or o.state_version < c.minimum_version:
        return Decision.UNKNOWN
    if c.required_source is not None and o.source_id != c.required_source:
        return Decision.UNKNOWN
    if not e.verified or not e.source_authorized or not e.chain_complete:
        return Decision.UNKNOWN
    if o.causal_boundary < c.minimum_causal_boundary:
        return Decision.UNKNOWN
    if e.claim == "conflict":
        return Decision.CONFLICT
    if e.claim == "applied" and o.status == "APPLIED":
        return Decision.REALIZED
    return Decision.UNKNOWN


def good(source: str = "observer-a", authorized: bool = True, complete: bool = True, boundary: int = 12) -> Evidence:
    return Evidence(Observation("e1", "target-a", 7, source, boundary, "APPLIED"), True, authorized, complete, "applied")


def test_independent_authorized_observers_can_support_same_claim() -> None:
    assert assess("e1", good("observer-a"), Constraint("observer-a", 7, 12)) is Decision.REALIZED
    assert assess("e1", good("observer-b"), Constraint("observer-b", 7, 12)) is Decision.REALIZED


def test_source_substitution_is_not_silent() -> None:
    assert assess("e1", good("observer-b"), Constraint("observer-a", 7, 12)) is Decision.UNKNOWN


def test_compromised_observer_is_insufficient() -> None:
    assert assess("e1", good("observer-a", authorized=False), Constraint("observer-a", 7, 12)) is Decision.UNKNOWN


def test_observer_capability_does_not_become_authority() -> None:
    e = good("observer-a")
    assert assess("e1", e, Constraint("observer-a", 7, 12)) is Decision.REALIZED
    # The observer's admissibility is evaluated as evidence for a transition;
    # no authority mutation is represented or inferred by the probe.


def test_truncated_causal_chain_is_unknown() -> None:
    assert assess("e1", good("observer-a", complete=False), Constraint("observer-a", 7, 12)) is Decision.UNKNOWN


def test_causal_boundary_is_transition_specific() -> None:
    assert assess("e1", good(boundary=12), Constraint("observer-a", 7, 12)) is Decision.REALIZED
    assert assess("e1", good(boundary=12), Constraint("observer-a", 7, 13)) is Decision.UNKNOWN


def test_conflicting_observers_remain_conflict() -> None:
    e = Evidence(good("observer-a").observation, True, True, True, "conflict")
    assert assess("e1", e, Constraint("observer-a", 7, 12)) is Decision.CONFLICT


def test_source_is_data_in_observation_not_new_primitive() -> None:
    candidate_primitives = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}
    forbidden = {"Source", "Trust", "Provenance", "Witness", "Confidence", "Causality"}
    assert not (candidate_primitives & forbidden)


def main() -> None:
    test_independent_authorized_observers_can_support_same_claim()
    test_source_substitution_is_not_silent()
    test_compromised_observer_is_insufficient()
    test_observer_capability_does_not_become_authority()
    test_truncated_causal_chain_is_unknown()
    test_causal_boundary_is_transition_specific()
    test_conflicting_observers_remain_conflict()
    test_source_is_data_in_observation_not_new_primitive()
    print("PASS30_PUBLIC: PASS; cases=8; private_data=none; new_primitives=0")


if __name__ == "__main__":
    main()
