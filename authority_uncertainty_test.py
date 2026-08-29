"""Executable checks for authority uncertainty."""

from authority_uncertainty import AuthorityState, Mechanism, admit, derive_state, verify


def test_invariants() -> None:
    verify()


def test_unknown_and_conflicting_are_distinct() -> None:
    assert derive_state(False, False) == AuthorityState.UNKNOWN
    assert derive_state(True, True) == AuthorityState.CONFLICTING
    assert AuthorityState.UNKNOWN != AuthorityState.REVOKED
    assert AuthorityState.CONFLICTING != AuthorityState.AUTHORIZED


def test_fail_closed_preserves_boundary() -> None:
    for state in (AuthorityState.UNKNOWN, AuthorityState.REVOKED, AuthorityState.CONFLICTING):
        assert admit(state, Mechanism.FAIL_CLOSED) is False


def test_optimism_is_the_counterexample() -> None:
    assert admit(AuthorityState.UNKNOWN, Mechanism.OPTIMISTIC) is True


if __name__ == "__main__":
    test_invariants()
    test_unknown_and_conflicting_are_distinct()
    test_fail_closed_preserves_boundary()
    test_optimism_is_the_counterexample()
    print("authority uncertainty: PASS")
