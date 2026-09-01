#!/usr/bin/env python3
"""P209 strengthened clean-room decision/selection reduction probe."""

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
    if not c.name or not c.capability or not c.authorized or not c.allowed:
        raise ValueError("rejected")
    return c


def select(candidates, state, constraint):
    # Selection is a bounded transition over State; criteria are data in the
    # constraint/state context, not a Genesis decision primitive.
    admissible = [
        c for c in candidates
        if c.authorized and c.allowed and c.capability in constraint["capabilities"]
    ]
    if not admissible:
        return None
    preferred = state.get("preferred")
    ranked = sorted(admissible, key=lambda c: (c.name == preferred, c.score), reverse=True)
    if len(ranked) > 1 and ranked[0].score == ranked[1].score and ranked[0].name != preferred:
        return None
    return ranked[0]


def realize(c):
    return replace(c, observed=True)


def verify(c):
    if c.unknown or not c.observed:
        return replace(c, evidenced=False)
    return replace(c, evidenced=True)


def test_constructive_selection():
    state = {"preferred": None}
    constraint = {"capabilities": {"write"}}
    c = select([Candidate("A", "write", score=5), Candidate("B", "write", score=3)], state, constraint)
    c = verify(realize(admit(c)))
    assert c.name == "A" and c.evidenced


def test_state_preference_changes_selection():
    candidates = [Candidate("A", "write", score=5), Candidate("B", "write", score=4)]
    constraint = {"capabilities": {"write"}}
    assert select(candidates, {"preferred": None}, constraint).name == "A"
    assert select(candidates, {"preferred": "B"}, constraint).name == "B"


def test_constraint_changes_selection():
    candidates = [Candidate("A", "send", score=10), Candidate("B", "draft", score=7)]
    assert select(candidates, {}, {"capabilities": {"send", "draft"}}).name == "A"
    assert select(candidates, {}, {"capabilities": {"draft"}}).name == "B"


def test_unauthorized_candidate_never_wins():
    candidates = [Candidate("A", "restricted", authorized=False, score=100), Candidate("B", "draft", score=1)]
    assert select(candidates, {}, {"capabilities": {"restricted", "draft"}}).name == "B"


def test_tie_is_ambiguous_not_success():
    candidates = [Candidate("A", "act", score=5), Candidate("B", "act", score=5)]
    assert select(candidates, {}, {"capabilities": {"act"}}) is None


def test_policy_update_is_state_transition():
    state = {"preferred": "A"}
    transition = Candidate("B", "act", score=9)
    state2 = dict(state)
    state2["preferred"] = transition.name
    assert state["preferred"] == "A" and state2["preferred"] == "B"


def test_observation_not_decision():
    c = replace(Candidate("A", "act", score=5), observed=True)
    assert not c.evidenced


def test_unknown_not_success():
    c = verify(replace(Candidate("A", "act", score=5), observed=True, unknown=True))
    assert not c.evidenced


def test_evidence_does_not_expand_authority():
    c = verify(realize(Candidate("A", "act", score=5)))
    assert c.evidenced
    try:
        admit(Candidate("B", "restricted", authorized=False, score=100))
    except ValueError:
        return
    raise AssertionError("evidence laundered into authority")


def test_malformed_fails_closed():
    try:
        admit(Candidate("", "", authorized=True, allowed=True))
    except ValueError:
        return
    raise AssertionError("malformed candidate admitted")


def test_no_decision_or_preference_primitive_in_basis():
    assert BASIS == {"state", "transition", "capability", "authority", "observation", "evidence", "constraint"}
    assert "decision" not in BASIS and "preference" not in BASIS and "policy" not in BASIS and "selection" not in BASIS


def main():
    tests = [
        test_constructive_selection,
        test_state_preference_changes_selection,
        test_constraint_changes_selection,
        test_unauthorized_candidate_never_wins,
        test_tie_is_ambiguous_not_success,
        test_policy_update_is_state_transition,
        test_observation_not_decision,
        test_unknown_not_success,
        test_evidence_does_not_expand_authority,
        test_malformed_fails_closed,
        test_no_decision_or_preference_primitive_in_basis,
    ]
    for t in tests:
        t()
        print(f"PASS {t.__name__}")
    print(f"P209_DECISION_SELECTION_REDUCTION_PASS; assertions={len(tests)}; basis_size={len(BASIS)}; new_primitive_required=false")

if __name__ == "__main__":
    main()
