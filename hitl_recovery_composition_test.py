"""Regression suite for HITL × recovery composition."""
from hitl_recovery_composition import Context, Decision, Effect, decide_initial, decide_recovery


def test_approval_does_not_make_unknown_verified():
    c = Context(True, Effect.UNKNOWN, True, "high", True, False, True)
    assert decide_recovery(c) is Decision.RETRY_UNSAFE


def test_verified_idempotency_can_make_same_identity_retry_safe():
    c = Context(True, Effect.UNKNOWN, True, "high", True, True, True)
    assert decide_recovery(c) is Decision.RETRY_SAFE


def test_partial_effect_remains_unsafe_after_approval():
    c = Context(True, Effect.PARTIAL, True, "high", True, True, True)
    assert decide_recovery(c) is Decision.RETRY_UNSAFE


def test_observed_effect_remains_unsafe_after_approval():
    c = Context(True, Effect.OBSERVED, True, "high", True, True, True)
    assert decide_recovery(c) is Decision.RETRY_UNSAFE


def test_revocation_overrides_prior_approval():
    c = Context(False, Effect.UNKNOWN, True, "high", True, True, True)
    assert decide_recovery(c) is Decision.BLOCK


def test_identity_change_blocks_safe_retry_claim():
    c = Context(True, Effect.UNKNOWN, True, "high", True, True, False)
    assert decide_recovery(c) is Decision.RETRY_UNSAFE


def test_initial_high_risk_without_approval_requires_hitl():
    c = Context(True, Effect.UNKNOWN, True, "high", False, False, True)
    assert decide_initial(c) is Decision.HITL_REQUIRED


def test_initial_approval_is_not_effect_evidence():
    c = Context(True, Effect.UNKNOWN, True, "high", True, False, True)
    assert decide_initial(c) is Decision.PROCEED
    assert decide_recovery(c) is Decision.RETRY_UNSAFE


def test_verified_no_effect_does_not_create_retry_safe_state():
    c = Context(True, Effect.NONE_VERIFIED, True, "high", True, True, True)
    assert decide_recovery(c) is Decision.RETRY_UNSAFE


def test_revocation_overrides_initial_approval():
    c = Context(False, Effect.UNKNOWN, True, "high", True, False, True)
    assert decide_initial(c) is Decision.BLOCK


def test_low_risk_unknown_can_be_initially_proceeded():
    c = Context(True, Effect.UNKNOWN, False, "low", False, False, True)
    assert decide_initial(c) is Decision.PROCEED


def test_harm_threshold_does_not_change_effect_state():
    c = Context(True, Effect.UNKNOWN, False, "high", True, False, True)
    assert decide_initial(c) is Decision.PROCEED
    assert decide_recovery(c) is Decision.RETRY_UNSAFE


def test_hitl_is_not_execution():
    c = Context(True, Effect.UNKNOWN, True, "high", True, False, True)
    assert decide_initial(c) is Decision.PROCEED
    assert c.effect is Effect.UNKNOWN


if __name__ == "__main__":
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for test in tests:
        test()
    print("HITL RECOVERY COMPOSITION REGRESSION 13/13 PASS")
