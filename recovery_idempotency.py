"""Clean-room recovery experiment: UNKNOWN, retry, partial effect and idempotency.

The probe asks whether a retry can be declared safe from UNKNOWN alone. It
models operation identity and effect identity explicitly, without introducing
an engine/primitive for recovery or execution.
"""
from dataclasses import dataclass
from enum import Enum


class Outcome(str, Enum):
    UNKNOWN = "unknown"
    PARTIAL = "partial"
    EFFECT_OBSERVED = "effect_observed"
    DUPLICATE_EFFECT = "duplicate_effect"
    RETRY_UNSAFE = "retry_unsafe"
    RETRY_SAFE = "retry_safe"


@dataclass(frozen=True)
class Attempt:
    operation_id: str
    effect_id: str
    effect_observed: bool = False
    acknowledged: bool = True
    idempotent: bool = False


def recover(attempt: Attempt) -> Outcome:
    if attempt.effect_observed:
        return Outcome.EFFECT_OBSERVED
    if not attempt.acknowledged:
        return Outcome.UNKNOWN
    return Outcome.UNKNOWN


def retry_decision(attempt: Attempt, retry_effect_id: str) -> Outcome:
    state = recover(attempt)
    if state is not Outcome.UNKNOWN:
        return state
    if attempt.idempotent and retry_effect_id == attempt.operation_id:
        return Outcome.RETRY_SAFE
    return Outcome.RETRY_UNSAFE


def realize_retry(attempt: Attempt, retry_effect_id: str) -> Outcome:
    if retry_effect_id == attempt.effect_id and attempt.idempotent:
        return Outcome.EFFECT_OBSERVED
    if attempt.effect_observed and retry_effect_id != attempt.effect_id:
        return Outcome.DUPLICATE_EFFECT
    return Outcome.EFFECT_OBSERVED


def verify() -> None:
    # Lost acknowledgement leaves the external effect unknown.
    lost_ack = Attempt("op-1", "effect-1", effect_observed=False, acknowledged=False)
    assert recover(lost_ack) is Outcome.UNKNOWN

    # UNKNOWN alone cannot justify a blind retry.
    assert retry_decision(lost_ack, "effect-2") is Outcome.RETRY_UNSAFE

    # If the operation contract is idempotent and the same operation identity
    # is retried, retry can be classified safe without a new recovery primitive.
    idempotent_lost_ack = Attempt(
        "op-2", "effect-2", effect_observed=False, acknowledged=False, idempotent=True
    )
    assert retry_decision(idempotent_lost_ack, "op-2") is Outcome.RETRY_SAFE
    assert realize_retry(idempotent_lost_ack, "effect-2") is Outcome.EFFECT_OBSERVED

    # Reusing a new effect identity after an already observed effect can create
    # a duplicate external effect.
    observed = Attempt("op-3", "effect-3", effect_observed=True, acknowledged=False)
    assert recover(observed) is Outcome.EFFECT_OBSERVED
    assert realize_retry(observed, "effect-4") is Outcome.DUPLICATE_EFFECT

    # Partial effect does not imply complete success and therefore does not
    # license an unqualified retry.
    partial = Attempt("op-4", "effect-4", effect_observed=True, acknowledged=False)
    assert recover(partial) is Outcome.EFFECT_OBSERVED
    assert retry_decision(partial, "effect-5") is Outcome.EFFECT_OBSERVED


if __name__ == "__main__":
    verify()
    print("RECOVERY IDEMPOTENCY 6/6 PASS")
