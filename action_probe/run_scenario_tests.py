from scenario_matrix import SCENARIOS, State, retry_policy


def main():
    revoked = next(s for s in SCENARIOS if s.name == "revoked_before_execution")
    assert revoked.expected == (State.REJECTED,)
    assert revoked.retry_allowed is False

    assert retry_policy(State.UNKNOWN) is False
    assert retry_policy(State.FAILED) is True

    partial = next(s for s in SCENARIOS if s.name == "partial_effect")
    assert State.PARTIAL in partial.expected
    assert State.UNKNOWN in partial.expected
    assert partial.retry_allowed is False

    success = next(s for s in SCENARIOS if s.name == "successful_execution")
    assert success.expected[-1] == State.VERIFIED

    print("EXECUTION_SCENARIO_MATRIX_OK")


if __name__ == "__main__":
    main()
