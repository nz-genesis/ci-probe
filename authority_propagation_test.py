"""Executable checks for authority propagation and reconciliation."""

from authority_propagation import (
    Admission,
    AuthorityState,
    DecisionContext,
    Observation,
    admit,
    derive_state,
    reconcile,
    verify,
)


def test_experiment_invariants() -> None:
    verify()


def test_stale_authorization_is_unknown_not_authorized() -> None:
    context = DecisionContext(10, 2, True, True)
    stale = Observation("A", AuthorityState.AUTHORIZED, 3, 3)
    assert derive_state((stale,), context) is AuthorityState.UNKNOWN
    assert admit(AuthorityState.UNKNOWN, context) is Admission.BLOCK


def test_current_revoke_blocks_even_with_approval() -> None:
    context = DecisionContext(10, 2, True, True)
    revoked = Observation("A", AuthorityState.REVOKED, 9, 9)
    assert derive_state((revoked,), context) is AuthorityState.REVOKED
    assert admit(AuthorityState.REVOKED, context) is Admission.BLOCK


def test_concurrent_current_evidence_is_conflicting() -> None:
    context = DecisionContext(10, 2, True, True)
    observations = (
        Observation("A", AuthorityState.REVOKED, 9, 9),
        Observation("B", AuthorityState.AUTHORIZED, 10, 10),
    )
    assert derive_state(observations, context) is AuthorityState.CONFLICTING
    assert admit(AuthorityState.CONFLICTING, context) is Admission.BLOCK


def test_pending_human_decision_is_not_authorization() -> None:
    context = DecisionContext(10, 2, False, True)
    assert admit(AuthorityState.AUTHORIZED, context) is Admission.PENDING


def test_late_revoke_reconciles_prior_authorized_observation() -> None:
    late = Observation("A", AuthorityState.REVOKED, 8, 12)
    assert reconcile(late, AuthorityState.AUTHORIZED) is AuthorityState.REVOKED


def test_late_authorization_after_revoke_is_not_silently_authorized() -> None:
    late = Observation("B", AuthorityState.AUTHORIZED, 8, 12)
    assert reconcile(late, AuthorityState.REVOKED) is AuthorityState.CONFLICTING


def test_malformed_causal_order_is_unknown() -> None:
    context = DecisionContext(10, 2, True, True)
    malformed = Observation("A", AuthorityState.AUTHORIZED, 20, 9)
    assert derive_state((malformed,), context) is AuthorityState.UNKNOWN


if __name__ == "__main__":
    test_experiment_invariants()
    test_stale_authorization_is_unknown_not_authorized()
    test_current_revoke_blocks_even_with_approval()
    test_concurrent_current_evidence_is_conflicting()
    test_pending_human_decision_is_not_authorization()
    test_late_revoke_reconciles_prior_authorized_observation()
    test_late_authorization_after_revoke_is_not_silently_authorized()
    test_malformed_causal_order_is_unknown()
    print("authority propagation: PASS")
