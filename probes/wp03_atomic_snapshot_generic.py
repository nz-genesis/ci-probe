"""Public-safe generic probe for atomic snapshot replacement and staged reservation.

This file contains no private project source, identifiers, fixtures, or semantics.
It tests only a general Python state-update technique. It does not test any
private scheduler implementation or product behavior.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Constraint:
    constraint_id: str
    capacity: int


def build_snapshot(constraints: tuple[Constraint, ...]) -> dict[str, Constraint]:
    staged: dict[str, Constraint] = {}
    for constraint in constraints:
        if constraint.constraint_id in staged:
            raise ValueError("duplicate constraint identity")
        staged[constraint.constraint_id] = constraint
    return staged


def replace_snapshot(
    active: dict[str, Constraint],
    constraints: tuple[Constraint, ...],
) -> dict[str, Constraint]:
    staged = build_snapshot(constraints)
    active.clear()
    active.update(staged)
    return active


def staged_reservations(
    active: dict[str, int],
    requests: tuple[tuple[str, int], ...],
    reserve,
) -> dict[str, int]:
    staged = dict(active)
    for key, amount in requests:
        staged[key] = reserve(staged[key], amount)
    active.clear()
    active.update(staged)
    return active


def test_duplicate_snapshot_rejected_without_mutation() -> None:
    original = {"old": Constraint("old", 7)}
    before = dict(original)
    try:
        replace_snapshot(
            original,
            (Constraint("new", 3), Constraint("new", 4)),
        )
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate snapshot unexpectedly accepted")
    assert original == before, "failed snapshot load mutated active state"


def test_valid_snapshot_replaces_complete_state() -> None:
    original = {"old": Constraint("old", 7)}
    replace_snapshot(original, (Constraint("new-a", 3), Constraint("new-b", 4)))
    assert original == {
        "new-a": Constraint("new-a", 3),
        "new-b": Constraint("new-b", 4),
    }


def test_second_reservation_failure_is_atomic() -> None:
    original = {"requests": 1, "cpu": 2}
    before = dict(original)
    calls = 0

    def reserve(current: int, amount: int) -> int:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("injected second-stage failure")
        return current + amount

    try:
        staged_reservations(original, (("requests", 1), ("cpu", 1)), reserve)
    except RuntimeError:
        pass
    else:
        raise AssertionError("injected reservation failure did not propagate")
    assert original == before, "failed reservation partially mutated active state"


def test_successful_reservations_commit_all_dimensions() -> None:
    original = {"requests": 1, "cpu": 2}
    staged_reservations(original, (("requests", 1), ("cpu", 3)), lambda a, b: a + b)
    assert original == {"requests": 2, "cpu": 5}


def main() -> None:
    tests = (
        test_duplicate_snapshot_rejected_without_mutation,
        test_valid_snapshot_replaces_complete_state,
        test_second_reservation_failure_is_atomic,
        test_successful_reservations_commit_all_dimensions,
    )
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print("WP03_GENERIC_ATOMICITY: PASS; cases=4; private_source=none; product_claim=none")


if __name__ == "__main__":
    main()
