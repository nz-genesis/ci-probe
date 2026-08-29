from recovery_idempotency import Attempt, Outcome, realize_retry, recover, retry_decision


def test_lost_ack_is_unknown():
    attempt = Attempt("op-1", "effect-1", effect_observed=False, acknowledged=False)
    assert recover(attempt) is Outcome.UNKNOWN


def test_unknown_does_not_make_blind_retry_safe():
    attempt = Attempt("op-1", "effect-1", effect_observed=False, acknowledged=False)
    assert retry_decision(attempt, "effect-2") is Outcome.RETRY_UNSAFE


def test_idempotent_same_operation_can_be_retried_safely():
    attempt = Attempt(
        "op-2", "effect-2", effect_observed=False, acknowledged=False, idempotent=True
    )
    assert retry_decision(attempt, "op-2") is Outcome.RETRY_SAFE
    assert realize_retry(attempt, "effect-2") is Outcome.EFFECT_OBSERVED


def test_new_effect_identity_after_observed_effect_can_duplicate():
    attempt = Attempt("op-3", "effect-3", effect_observed=True, acknowledged=False)
    assert realize_retry(attempt, "effect-4") is Outcome.DUPLICATE_EFFECT


def test_observed_partial_or_external_effect_is_not_unknown():
    attempt = Attempt("op-4", "effect-4", effect_observed=True, acknowledged=False)
    assert recover(attempt) is Outcome.EFFECT_OBSERVED
    assert retry_decision(attempt, "effect-5") is Outcome.EFFECT_OBSERVED


def test_idempotency_is_bound_to_operation_identity():
    attempt = Attempt(
        "op-5", "effect-5", effect_observed=False, acknowledged=False, idempotent=True
    )
    assert retry_decision(attempt, "op-6") is Outcome.RETRY_UNSAFE
