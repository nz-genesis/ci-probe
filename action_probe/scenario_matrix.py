"""Generic execution scenario matrix with explicit effect certainty."""
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
    RECONCILED = "reconciled"
    UNRESOLVED = "unresolved"


class EffectCertainty(str, Enum):
    NOT_ATTEMPTED = "not_attempted"
    NO_EFFECT_CONFIRMED = "no_effect_confirmed"
    POSSIBLE = "possible"
    PARTIAL = "partial"
    CONFIRMED = "confirmed"


@dataclass(frozen=True)
class Scenario:
    name: str
    initial: State
    expected: tuple[State, ...]
    effect_certainty: EffectCertainty
    new_operation_retry_candidate: bool


SCENARIOS = (
    Scenario("revoked_before_execution", State.ADMITTED, (State.REJECTED,), EffectCertainty.NO_EFFECT_CONFIRMED, False),
    Scenario("successful_execution", State.ADMITTED, (State.EXECUTED, State.VERIFIED), EffectCertainty.CONFIRMED, False),
    Scenario("partial_effect", State.ADMITTED, (State.PARTIAL, State.UNKNOWN), EffectCertainty.PARTIAL, False),
    Scenario("lost_acknowledgement", State.ADMITTED, (State.UNKNOWN,), EffectCertainty.POSSIBLE, False),
    Scenario("failed_before_effect", State.ADMITTED, (State.FAILED,), EffectCertainty.NO_EFFECT_CONFIRMED, True),
    Scenario("failed_after_possible_effect", State.ADMITTED, (State.FAILED,), EffectCertainty.POSSIBLE, False),
    Scenario("reconciled_not_applied", State.UNKNOWN, (State.RECONCILED,), EffectCertainty.NO_EFFECT_CONFIRMED, True),
    Scenario("reconciliation_unresolved", State.UNKNOWN, (State.UNRESOLVED,), EffectCertainty.POSSIBLE, False),
)


def new_operation_retry_candidate(state: State, effect_certainty: EffectCertainty) -> bool:
    """Candidate only; a new identity and fresh admission are still required."""
    return state in {State.FAILED, State.RECONCILED} and effect_certainty == EffectCertainty.NO_EFFECT_CONFIRMED
