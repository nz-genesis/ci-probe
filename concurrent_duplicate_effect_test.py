"""Regression suite for the bounded L6h concurrent duplicate-effect probe."""
from concurrent_duplicate_effect import (
    Operation,
    Outcome,
    RealizerAttempt,
    realize_concurrently,
    retry_decision,
    state,
)


def test_unknown_is_not_failure_or_success() -> None:
    attempt = RealizerAttempt("A", "op", "a1", "e1", False, False)
    assert state(attempt) is Outcome.UNKNOWN


def test_two_distinct_effect_ids_are_duplicate_risk() -> None:
    op = Operation("op", "r", "v1", True, "r")
    a = RealizerAttempt("A", "op", "a1", "e1", False, False)
    b = RealizerAttempt("B", "op", "b1", "e2", False, False)
    assert realize_concurrently(op, a, b) is Outcome.DUPLICATE_EFFECT


def test_unverified_idempotency_blocks_retry() -> None:
    op = Operation("op", "r", "v1", True, "r")
    a = RealizerAttempt("A", "op", "a1", "e1", False, False)
    assert retry_decision(op, a, "v1", False) is Outcome.RETRY_UNSAFE


def test_version_drift_blocks_prior_idempotency_scope() -> None:
    op = Operation("op", "r", "v1", True, "r")
    a = RealizerAttempt("A", "op", "a1", "e1", False, False)
    assert retry_decision(op, a, "v2", True) is Outcome.RETRY_UNSAFE


def test_same_effect_identity_is_only_a_bounded_observation() -> None:
    op = Operation("op", "r", "v1", True, "r")
    a = RealizerAttempt("A", "op", "a1", "e1", False, False)
    b = RealizerAttempt("B", "op", "b1", "e1", False, False)
    assert realize_concurrently(op, a, b) is Outcome.EFFECT_OBSERVED
