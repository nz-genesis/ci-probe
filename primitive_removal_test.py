"""Executable checks for the primitive-removal experiment."""

from primitive_removal import (
    AT_MOST_ONCE,
    NO_EFFECT_CARDINALITY_CONSTRAINT,
    REQUEST,
    State,
    run_two_attempts,
    verify,
)


def test_reduction_invariants() -> None:
    verify()


def test_named_primitive_is_not_needed() -> None:
    state = run_two_attempts(AT_MOST_ONCE)
    assert isinstance(state, State)
    assert state.value == REQUEST.value
    assert state.effect_count == 1


def test_removing_the_guarantee_causes_semantic_loss() -> None:
    state = run_two_attempts(NO_EFFECT_CARDINALITY_CONSTRAINT)
    assert state.value == REQUEST.value
    assert state.effect_count == 2


if __name__ == "__main__":
    test_reduction_invariants()
    test_named_primitive_is_not_needed()
    test_removing_the_guarantee_causes_semantic_loss()
    print("primitive removal: PASS")
