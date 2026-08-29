"""Executable checks for the recovery matrix."""

from recovery_matrix import FAULTS, Status, run_matrix, safe_retry_from_status, verify_invariants


def test_all_recovery_conditions_are_exercised() -> None:
    verify_invariants()
    observed = {direct.status for direct, _ in run_matrix()}
    expected = {fault.status for fault in FAULTS}
    assert observed == expected


def test_direct_and_queued_have_same_bounded_classification() -> None:
    for direct, queued in run_matrix():
        assert direct.status == queued.status
        assert direct.request_id == queued.request_id
        assert direct.effect_count == queued.effect_count
        assert direct.observed_values == queued.observed_values


def test_partial_is_genuinely_partial() -> None:
    partial = next(direct for direct, _ in run_matrix() if direct.status == Status.PARTIAL)
    assert partial.effect_count == 1
    assert partial.observed_values == ("v1", "v0")


def test_ambiguous_states_require_reconciliation() -> None:
    for direct, _ in run_matrix():
        if direct.status in (Status.PARTIAL, Status.UNKNOWN, Status.DUPLICATE):
            assert direct.reconciliation_required is True


def test_unknown_is_not_failed_and_not_blind_retryable() -> None:
    assert Status.UNKNOWN != Status.FAILED
    assert safe_retry_from_status(Status.UNKNOWN) is False


if __name__ == "__main__":
    test_all_recovery_conditions_are_exercised()
    test_direct_and_queued_have_same_bounded_classification()
    test_partial_is_genuinely_partial()
    test_ambiguous_states_require_reconciliation()
    test_unknown_is_not_failed_and_not_blind_retryable()
    print("recovery matrix: PASS")
