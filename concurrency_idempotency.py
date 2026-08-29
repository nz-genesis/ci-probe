"""Clean-room concurrency/idempotency experiment.

The experiment separates two contracts:

1. final-state contract: the requested state is established;
2. effect-count contract: the request produces at most one external effect.

Two mechanisms are compared: naive application and request-key deduplication.
The same concurrent/retry schedules are enumerated deterministically.
"""

from dataclasses import dataclass
from enum import Enum


class Mechanism(str, Enum):
    NAIVE = "naive"
    DEDUPLICATING = "deduplicating"


@dataclass(frozen=True)
class Request:
    request_id: str
    value: str


@dataclass(frozen=True)
class Result:
    mechanism: Mechanism
    schedule: tuple[str, ...]
    final_value: str | None
    effect_count: int
    duplicate_prevented: bool


REQUEST = Request("req-001", "v1")


class Realizer:
    def __init__(self, mechanism: Mechanism) -> None:
        self.mechanism = mechanism
        self.value: str | None = None
        self.effect_count = 0
        self.seen: set[str] = set()

    def attempt(self, request: Request) -> bool:
        if self.mechanism is Mechanism.DEDUPLICATING and request.request_id in self.seen:
            return False
        self.seen.add(request.request_id)
        self.value = request.value
        self.effect_count += 1
        return True


def run_schedule(mechanism: Mechanism, schedule: tuple[str, ...]) -> Result:
    realizer = Realizer(mechanism)
    for label in schedule:
        if label == "attempt-1":
            realizer.attempt(REQUEST)
        elif label == "attempt-2":
            realizer.attempt(REQUEST)
        else:
            raise ValueError(label)
    return Result(
        mechanism,
        schedule,
        realizer.value,
        realizer.effect_count,
        realizer.effect_count < len(schedule),
    )


def concurrent_schedules() -> tuple[tuple[str, ...], ...]:
    return (("attempt-1", "attempt-2"), ("attempt-2", "attempt-1"))


def run_retry_after_lost_ack() -> tuple[Result, Result]:
    schedule = ("initial-attempt", "retry-after-unknown")
    results: list[Result] = []
    for mechanism in Mechanism:
        realizer = Realizer(mechanism)
        realizer.attempt(REQUEST)
        realizer.attempt(REQUEST)
        results.append(
            Result(
                mechanism,
                schedule,
                realizer.value,
                realizer.effect_count,
                realizer.effect_count == 1,
            )
        )
    return results[0], results[1]


def verify() -> None:
    for schedule in concurrent_schedules():
        naive = run_schedule(Mechanism.NAIVE, schedule)
        dedup = run_schedule(Mechanism.DEDUPLICATING, schedule)

        # Both satisfy a final-state-only contract.
        assert naive.final_value == dedup.final_value == "v1"

        # Only deduplication satisfies the stronger at-most-once-effect contract.
        assert naive.effect_count == 2
        assert dedup.effect_count == 1
        assert dedup.duplicate_prevented is True

    naive_retry, dedup_retry = run_retry_after_lost_ack()
    assert naive_retry.final_value == dedup_retry.final_value == "v1"
    assert naive_retry.effect_count == 2
    assert dedup_retry.effect_count == 1
    assert dedup_retry.duplicate_prevented is True


if __name__ == "__main__":
    verify()
    print("concurrency/idempotency: PASS")
