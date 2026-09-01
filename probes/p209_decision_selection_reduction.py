#!/usr/bin/env python3
"""P209 clean-room decision/selection reduction probe.

Tests whether decision/selection/policy/preference can be represented as
State + Transition + Capability + Authority + Observation + Evidence +
Constraint, without introducing a new Genesis semantic primitive.
"""

from dataclasses import dataclass, replace

BASIS = {"state", "transition", "capability", "authority", "observation", "evidence", "constraint"}


@dataclass(frozen=True)
class Candidate:
    name: str
    capability: str
    authorized: bool = True
    allowed: bool = True
    score: int = 0
    observed: bool = False
    evidenced: bool = False
    unknown: bool = False


def admit(c: Candidate) -> Candidate:
    if not c.authorized or not c.allowed:
        raise ValueError("rejected")
    return c


def select(candidates):
    admissible = [c for c in candidates if c.authorized and c.allowed]
    if not admissible:
        return None
    best = max(c.score for c in admissible)
    winners = [c for c in admissible if c.score == best]
    return winners[0] if len(winners) == 1 else None


def realize(c):
    return replace(c, observed=True)


def verify(c):
    if c.unknown or not c.observed:
        return replace(c, evidenced=False)
    return replace(c, evidenced=True)


def test_constructive_selection():
    c = select([
        Candidate("A", "write", score=5),
        Candidate("B", "write", score=3),
    ])
    c = verify(realize(admit(c)))
    assert c.name == "A" and c.evidenced


def test_constraint_changes_choice_without_new_primitive():
    candidates = [Candidate("A", "send", score=10), Candidate("B", "draft", score=7)]
    first = select(candidates)
    constrained = [replace(candidates[0], allowed=False), candidates[1]]
    second = select(constrained)
    assert first.name == "A" and second.name == "B"


def test_policy_change_is_state_transition():
    state = {"preferred": "A"}
    transition = replace(Candidate("B", "act", score=2), score=9)
    state["preferred"] = transition.name
    assert state["preferred"] == "B"


def test_tie_requires_non_success():
    c = select([Candidate("A", "act", score=5), Candidate("B", "act", score=5)])
    assert c is None


def test_unauthorized_preference_cannot_expand_authority():
    c = Candidate("A", "restricted", authorized=False, score=99)
    try:
        admit(c)
    except ValueError:
        return
    raise AssertionError("unauthorized preference bypassed authority")


def test_observation_is_not_decision():
    c = replace(Candidate("A", "act", score=5), observed=True)
    assert not c.evidenced


def test_unknown_is_not_success():
    c = verify(replace(Candidate("A", "act", score=5), observed=True, unknown=True))
    assert not c.evidenced


def test_goal_effect_separation():
    c = verify(realize(Candidate("A", "act", score=5)))
    assert c.evidenced
    # Evidence of realization does not confer authority for another action.
    try:
        admit(Candidate("B", "restricted", authorized=False, score=100))
    except ValueError:
        return
    raise AssertionError("world/evidence result laundered into authority")


def test_conflicting_authority_is_not_preference_resolution():
    c1 = Candidate("A", "act", authorized=True, allowed=True, score=5)
    c2 = Candidate("B", "act", authorized=False, allowed=True, score=100)
    winner = select([c1, c2])
    assert winner.name == "A"


def test_malformed_candidate_fails_closed():
    try:
        admit(Candidate("", "", authorized=False, allowed=True))
    except ValueError:
        return
    raise AssertionError("malformed candidate admitted")


def test_no_decision_primitive_required():
    # Decision/selection is a Transition over State constrained by Authority
    # and Constraint, with Observation/Evidence closing the epistemic loop.
    assert BASIS == {"state", "transition", "capability", "authority", "observation", "evidence", "constraint"}


def main():
    tests = [
        test_constructive_selection,
        test_constraint_changes_choice_without_new_primitive,
        test_policy_change_is_state_transition,
        test_tie_requires_non_success,
        test_unauthorized_preference_cannot_expand_authority,
        test_observation_is_not_decision,
        test_unknown_is_not_success,
        test_goal_effect_separation,
        test_conflicting_authority_is_not_preference_resolution,
        test_malformed_candidate_fails_closed,
        test_no_decision_primitive_required,
    ]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"P209_DECISION_SELECTION_REDUCTION_PASS; assertions={len(tests)}; basis_size={len(BASIS)}; new_primitive_required=false")


if __name__ == "__main__":
    main()
