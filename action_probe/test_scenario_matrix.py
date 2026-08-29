from action_probe.scenario_matrix import SCENARIOS, State, retry_policy


def test_revocation_blocks_execution():
    scenario = next(s for s in SCENARIOS if s.name == "revoked_before_execution")
    assert scenario.expected == (State.REJECTED,)
    assert scenario.retry_allowed is False


def test_unknown_never_gets_blind_retry():
    assert retry_policy(State.UNKNOWN) is False
    assert retry_policy(State.FAILED) is True


def test_partial_effect_requires_reconciliation():
    scenario = next(s for s in SCENARIOS if s.name == "partial_effect")
    assert State.PARTIAL in scenario.expected
    assert State.UNKNOWN in scenario.expected
    assert scenario.retry_allowed is False


def test_success_requires_verification():
    scenario = next(s for s in SCENARIOS if s.name == "successful_execution")
    assert scenario.expected[-1] == State.VERIFIED
