"""Clean-room L6h experiment: concurrent UNKNOWN recovery across realizers.

The probe tests whether two independent realizers can both act on the same
UNKNOWN operation and create a duplicate external effect. It deliberately
models no execution/recovery engine and treats authority, identity,
effect-observation and realization as separate facts.
"""
from dataclasses import dataclass
from enum import Enum


class Outcome(str, Enum):
    UNKNOWN = "unknown"
    EFFECT_OBSERVED = "effect_observed"
    DUPLICATE_EFFECT = "duplicate_effect"
    RETRY_UNSAFE = "retry_unsafe"
    RETRY_SAFE = "retry_safe"


@dataclass(frozen=True)
class Operation:
    operation_id: str
    resource_id: str
    resource_version: str
    idempotent: bool
    idempotency_scope: str


@dataclass(frozen=True)
class RealizerAttempt:
    realizer_id: str
    operation_id: str
    attempt_id: str
    effect_id: str
    acknowledgement: bool
    effect_observed: bool


def state(attempt: RealizerAttempt) -> Outcome:
    if attempt.effect_observed:
        return Outcome.EFFECT_OBSERVED
    if not attempt.acknowledgement:
        return Outcome.UNKNOWN
    return Outcome.UNKNOWN


def retry_decision(
    operation: Operation,
    attempt: RealizerAttempt,
    current_resource_version: str,
    verified_idempotency: bool,
) -> Outcome:
    if state(attempt) is not Outcome.UNKNOWN:
        return state(attempt)
    same_scope = operation.idempotency_scope == operation.resource_id
    same_version = operation.resource_version == current_resource_version
    if verified_idempotency and operation.idempotent and same_scope and same_version:
        return Outcome.RETRY_SAFE
    return Outcome.RETRY_UNSAFE


def realize_concurrently(
    operation: Operation,
    first: RealizerAttempt,
    second: RealizerAttempt,
) -> Outcome:
    # A second distinct effect identity after the first external effect is
    # established is a duplicate effect, regardless of the realizers involved.
    if first.effect_id != second.effect_id:
        return Outcome.DUPLICATE_EFFECT
    return Outcome.EFFECT_OBSERVED


def verify() -> None:
    op = Operation("op-1", "resource-1", "v1", True, "resource-1")
    a = RealizerAttempt("realizer-A", "op-1", "attempt-A", "effect-A", False, False)
    b = RealizerAttempt("realizer-B", "op-1", "attempt-B", "effect-B", False, False)

    # Both realizers independently observe UNKNOWN; neither may infer success.
    assert state(a) is Outcome.UNKNOWN
    assert state(b) is Outcome.UNKNOWN

    # Verified idempotency and matching scope/version can make a retry decision
    # safe as a decision property, but it does not erase concurrency risk.
    assert retry_decision(op, a, "v1", True) is Outcome.RETRY_SAFE
    assert retry_decision(op, b, "v1", True) is Outcome.RETRY_SAFE

    # If both actually realize distinct effects, the composition produces a
    # duplicate external effect. This is not hidden by the safe retry label.
    assert realize_concurrently(op, a, b) is Outcome.DUPLICATE_EFFECT

    # Without verified idempotency, UNKNOWN remains unsafe.
    assert retry_decision(op, a, "v1", False) is Outcome.RETRY_UNSAFE

    # Resource-version drift invalidates the applicability of the prior claim.
    assert retry_decision(op, a, "v2", True) is Outcome.RETRY_UNSAFE

    # Distinct operation identities are not interchangeable.
    other = Operation("op-2", "resource-1", "v1", True, "resource-1")
    other_attempt = RealizerAttempt("realizer-B", "op-2", "attempt-C", "effect-C", False, False)
    assert retry_decision(other, other_attempt, "v1", True) is Outcome.RETRY_SAFE
    assert other.operation_id != op.operation_id

    # Same effect identity is observationally one effect in this bounded model.
    b_same = RealizerAttempt("realizer-B", "op-1", "attempt-B2", "effect-A", False, False)
    assert realize_concurrently(op, a, b_same) is Outcome.EFFECT_OBSERVED


if __name__ == "__main__":
    verify()
    print("CONCURRENT DUPLICATE EFFECT 7/7 PASS")
