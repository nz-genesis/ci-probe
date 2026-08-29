"""Generic, Genesis-agnostic execution scenario matrix.

This file is deliberately a public clean-room test fixture. It models
observable execution states without importing or describing Genesis internals.
"""

from dataclasses import dataclass
from enum import Enum


class State(str, Enum):
    ADMITTED = "admitted"
    EXECUTED = "executed"
    PARTIAL = "partial"
    UNKNOWN = "unknown"
    VERIFIED = "verified"
    FAILED = "failed"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Scenario:
    name: str
    initial: State
    expected: tuple[State, ...]
    retry_allowed: bool


SCENARIOS = (
    Scenario("revoked_before_execution", State.ADMITTED, (State.REJECTED,), False),
    Scenario("successful_execution", State.ADMITTED, (State.EXECUTED, State.VERIFIED), False),
    Scenario("partial_effect", State.ADMITTED, (State.PARTIAL, State.UNKNOWN), False),
    Scenario("lost_acknowledgement", State.ADMITTED, (State.UNKNOWN,), False),
    Scenario("failed_before_effect", State.ADMITTED, (State.FAILED,), True),
)


def retry_policy(state: State) -> bool:
    """Return whether a retry is safe from state alone.

    UNKNOWN is intentionally never retryable from local state alone: an
    independent reconciliation step is required before choosing recovery.
    """
    return state == State.FAILED
