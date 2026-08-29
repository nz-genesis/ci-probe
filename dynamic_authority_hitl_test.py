"""Executable checks for dynamic authority + HITL experiment."""

from dynamic_authority_hitl import (
    Mechanism,
    Outcome,
    APPROVED_NO_REVOCATION,
    LATE_ACK_LOST_AFTER_EFFECT,
    PENDING_HUMAN,
    REVOKED_BEFORE_REALIZATION,
    realize,
    verify,
)


def test_experiment_invariants() -> None:
    verify()


def test_revocation_race_is_mechanism_discriminating() -> None:
    snapshot = realize(REVOKED_BEFORE_REALIZATION, Mechanism.SNAPSHOT)
    revalidate = realize(REVOKED_BEFORE_REALIZATION, Mechanism.REVALIDATE)
    assert snapshot.outcome == Outcome.EXECUTED
    assert revalidate.outcome == Outcome.BLOCKED_REVOKED


def test_human_approval_does_not_override_late_revocation() -> None:
    decision = realize(REVOKED_BEFORE_REALIZATION, Mechanism.REVALIDATE)
    assert decision.outcome == Outcome.BLOCKED_REVOKED
    assert decision.effect_count == 0


def test_pending_human_is_not_execution() -> None:
    decision = realize(PENDING_HUMAN, Mechanism.REVALIDATE)
    assert decision.outcome == Outcome.PENDING_HUMAN
    assert decision.effect_count == 0


def test_late_missing_ack_requires_reconciliation() -> None:
    decision = realize(LATE_ACK_LOST_AFTER_EFFECT, Mechanism.REVALIDATE)
    assert decision.outcome == Outcome.UNKNOWN_AFTER_EFFECT
    assert decision.reconciliation_required is True


def test_stable_authority_remains_mechanism_independent() -> None:
    snapshot = realize(APPROVED_NO_REVOCATION, Mechanism.SNAPSHOT)
    revalidate = realize(APPROVED_NO_REVOCATION, Mechanism.REVALIDATE)
    assert snapshot.outcome == revalidate.outcome == Outcome.EXECUTED


if __name__ == "__main__":
    test_experiment_invariants()
    test_revocation_race_is_mechanism_discriminating()
    test_human_approval_does_not_override_late_revocation()
    test_pending_human_is_not_execution()
    test_late_missing_ack_requires_reconciliation()
    test_stable_authority_remains_mechanism_independent()
    print("dynamic authority + HITL: PASS")
