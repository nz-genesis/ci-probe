"""Executable checks for the concurrency/idempotency experiment."""

from concurrency_idempotency import (
    Mechanism,
    concurrent_schedules,
    run_retry_after_lost_ack,
    run_schedule,
    verify,
)


def test_experiment_invariants() -> None:
    verify()


def test_both_orderings_expose_the_same_duplicate_effect() -> None:
    for schedule in concurrent_schedules():
        naive = run_schedule(Mechanism.NAIVE, schedule)
        dedup = run_schedule(Mechanism.DEDUPLICATING, schedule)
        assert naive.effect_count == 2
        assert dedup.effect_count == 1
        assert naive.final_value == dedup.final_value == "v1"


def test_lost_ack_retry_is_discriminating() -> None:
    naive, dedup = run_retry_after_lost_ack()
    assert naive.effect_count == 2
    assert dedup.effect_count == 1
    assert naive.final_value == dedup.final_value == "v1"


if __name__ == "__main__":
    test_experiment_invariants()
    test_both_orderings_expose_the_same_duplicate_effect()
    test_lost_ack_retry_is_discriminating()
    print("concurrency/idempotency: PASS")
