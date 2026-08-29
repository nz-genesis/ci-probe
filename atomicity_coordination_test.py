"""Regression suite for the bounded L6i atomicity/coordination probe."""
from atomicity_coordination import (
    Attempt,
    Contract,
    Outcome,
    realize_with_atomic_idempotency,
    realize_with_shared_coordination,
    realize_without_guarantee,
)


def test_two_mechanisms_same_contract_same_outcome() -> None:
    c = Contract("op", "r", "v1", True)
    a = Attempt("A", "e1")
    b = Attempt("B", "e2")
    assert realize_with_atomic_idempotency(c, a, b) is Outcome.SINGLE_EFFECT
    assert realize_with_shared_coordination(c, a, b) is Outcome.SINGLE_EFFECT


def test_removing_guarantee_exposes_duplicate_effect() -> None:
    c = Contract("op", "r", "v1", False)
    a = Attempt("A", "e1")
    b = Attempt("B", "e2")
    assert realize_without_guarantee(c, a, b) is Outcome.DUPLICATE_EFFECT


def test_missing_guarantee_is_not_silently_assumed() -> None:
    c = Contract("op", "r", "v1", False)
    a = Attempt("A", "e1")
    b = Attempt("B", "e2")
    assert realize_with_atomic_idempotency(c, a, b) is Outcome.CONTRACT_UNVERIFIED
    assert realize_with_shared_coordination(c, a, b) is Outcome.CONTRACT_UNVERIFIED


def test_contract_scope_is_operation_specific() -> None:
    c1 = Contract("op-1", "r", "v1", True)
    c2 = Contract("op-2", "r", "v1", True)
    assert c1.operation_id != c2.operation_id


def test_version_change_requires_reassessment() -> None:
    c = Contract("op", "r", "v2", False)
    a = Attempt("A", "e1")
    b = Attempt("B", "e2")
    assert realize_with_atomic_idempotency(c, a, b) is Outcome.CONTRACT_UNVERIFIED
