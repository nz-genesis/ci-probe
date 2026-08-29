"""Clean-room composition probe: HITL approval × recovery/effect uncertainty.

The probe asks whether human approval changes authority/risk acceptance without
collapsing UNKNOWN, PARTIAL_EFFECT, or retry safety into a single state.
"""
from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    PROCEED = "proceed"
    HITL_REQUIRED = "hitl_required"
    BLOCK = "block"
    RETRY_UNSAFE = "retry_unsafe"
    RETRY_SAFE = "retry_safe"


class Effect(str, Enum):
    NONE_VERIFIED = "none_verified"
    UNKNOWN = "unknown"
    PARTIAL = "partial"
    OBSERVED = "observed"


@dataclass(frozen=True)
class Context:
    authority_valid: bool
    effect: Effect
    irreversible: bool
    harm: str
    approval_valid: bool
    idempotency_verified: bool
    same_operation_identity: bool


def decide_initial(c: Context) -> Decision:
    if not c.authority_valid:
        return Decision.BLOCK
    if c.effect in {Effect.OBSERVED, Effect.PARTIAL}:
        return Decision.BLOCK
    if c.approval_valid:
        return Decision.PROCEED
    if c.harm == "high" or c.irreversible:
        return Decision.HITL_REQUIRED
    return Decision.PROCEED


def decide_recovery(c: Context) -> Decision:
    if not c.authority_valid:
        return Decision.BLOCK
    if c.effect in {Effect.OBSERVED, Effect.PARTIAL}:
        return Decision.RETRY_UNSAFE
    if c.effect is Effect.UNKNOWN:
        if c.idempotency_verified and c.same_operation_identity:
            return Decision.RETRY_SAFE
        return Decision.RETRY_UNSAFE
    return Decision.RETRY_UNSAFE


def verify() -> None:
    base = Context(True, Effect.UNKNOWN, False, "low", False, False, True)
    approved = Context(True, Effect.UNKNOWN, True, "high", True, False, True)
    approved_idempotent = Context(True, Effect.UNKNOWN, True, "high", True, True, True)
    partial = Context(True, Effect.PARTIAL, True, "high", True, True, True)
    observed = Context(True, Effect.OBSERVED, True, "high", True, True, True)
    revoked = Context(False, Effect.UNKNOWN, True, "high", True, True, True)
    changed_identity = Context(True, Effect.UNKNOWN, True, "high", True, True, False)
    verified_none = Context(True, Effect.NONE_VERIFIED, True, "high", True, True, True)

    assert decide_initial(base) is Decision.PROCEED
    assert decide_initial(approved) is Decision.PROCEED
    assert decide_initial(revoked) is Decision.BLOCK
    assert decide_initial(partial) is Decision.BLOCK
    assert decide_initial(observed) is Decision.BLOCK
    assert decide_initial(Context(True, Effect.UNKNOWN, True, "high", False, False, True)) is Decision.HITL_REQUIRED

    assert decide_recovery(approved) is Decision.RETRY_UNSAFE
    assert decide_recovery(approved_idempotent) is Decision.RETRY_SAFE
    assert decide_recovery(partial) is Decision.RETRY_UNSAFE
    assert decide_recovery(observed) is Decision.RETRY_UNSAFE
    assert decide_recovery(revoked) is Decision.BLOCK
    assert decide_recovery(changed_identity) is Decision.RETRY_UNSAFE
    assert decide_recovery(verified_none) is Decision.RETRY_UNSAFE


if __name__ == "__main__":
    verify()
    print("HITL RECOVERY COMPOSITION 13/13 PASS")
