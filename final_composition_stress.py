"""Generic clean-room stress model for HITL/recovery composition."""

from dataclasses import dataclass
from enum import Enum


class Authority(Enum):
    ACTIVE = "ACTIVE"
    REVOKED = "REVOKED"


class Approval(Enum):
    NONE = "NONE"
    VALID = "VALID"
    STALE = "STALE"
    CONFLICTING = "CONFLICTING"


class Effect(Enum):
    NONE = "NONE"
    UNKNOWN = "UNKNOWN"
    PARTIAL = "PARTIAL"
    OBSERVED = "OBSERVED"


class Decision(Enum):
    AUTO_PROCEED = "AUTO_PROCEED"
    HITL_REQUIRED = "HITL_REQUIRED"
    APPROVED = "APPROVED"
    BLOCK = "BLOCK"
    RETRY_SAFE = "RETRY_SAFE"
    RETRY_UNSAFE = "RETRY_UNSAFE"


@dataclass(frozen=True)
class Case:
    authority_at_approval: Authority
    authority_now: Authority
    approval: Approval
    effect: Effect
    verified_idempotency: bool
    same_identity: bool
    same_resource_version: bool
    concurrent_realizers: bool
    irreversible: bool


def initial_decision(c: Case) -> Decision:
    if c.authority_now is Authority.REVOKED:
        return Decision.BLOCK
    if c.approval in (Approval.STALE, Approval.CONFLICTING):
        return Decision.BLOCK
    if c.approval is Approval.NONE:
        return Decision.HITL_REQUIRED if c.irreversible else Decision.AUTO_PROCEED
    return Decision.APPROVED


def recovery_decision(c: Case) -> Decision:
    if c.authority_now is Authority.REVOKED:
        return Decision.BLOCK
    if c.approval is not Approval.VALID:
        return Decision.RETRY_UNSAFE
    if not c.same_resource_version:
        return Decision.BLOCK
    if not c.same_identity:
        return Decision.RETRY_UNSAFE
    if c.effect in (Effect.PARTIAL, Effect.OBSERVED):
        return Decision.RETRY_UNSAFE
    if c.effect is Effect.UNKNOWN:
        if c.verified_idempotency:
            return Decision.RETRY_SAFE
        return Decision.RETRY_UNSAFE
    return Decision.RETRY_UNSAFE


def main() -> None:
    cases = [
        # Approval survives only while current authority and scope remain valid.
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, True, True, True, False, True), Decision.APPROVED, Decision.RETRY_SAFE),
        (Case(Authority.ACTIVE, Authority.REVOKED, Approval.VALID, Effect.UNKNOWN, True, True, True, False, True), Decision.BLOCK, Decision.BLOCK),
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, True, True, False, False, True), Decision.APPROVED, Decision.BLOCK),
        # Human approval cannot turn partial/observed effect into safe retry.
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.PARTIAL, True, True, True, False, True), Decision.APPROVED, Decision.RETRY_UNSAFE),
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.OBSERVED, True, True, True, False, True), Decision.APPROVED, Decision.RETRY_UNSAFE),
        # UNKNOWN requires independently verified idempotency.
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, False, True, True, False, True), Decision.APPROVED, Decision.RETRY_UNSAFE),
        # Concurrent realizers do not create a new semantic primitive when the guarantee is verified.
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, True, True, True, True, True), Decision.APPROVED, Decision.RETRY_SAFE),
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, False, True, True, True, True), Decision.APPROVED, Decision.RETRY_UNSAFE),
        # Stale/conflicting approval is not authority.
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.STALE, Effect.UNKNOWN, True, True, True, False, True), Decision.BLOCK, Decision.RETRY_UNSAFE),
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.CONFLICTING, Effect.UNKNOWN, True, True, True, False, True), Decision.BLOCK, Decision.RETRY_UNSAFE),
        # Identity mismatch cannot inherit approval or idempotency.
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, True, False, True, False, True), Decision.APPROVED, Decision.RETRY_UNSAFE),
        # No approval remains a policy/authority decision, not an execution primitive.
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.NONE, Effect.NONE, False, False, True, False, True), Decision.HITL_REQUIRED, Decision.RETRY_UNSAFE),
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.NONE, Effect.NONE, False, False, True, False, False), Decision.AUTO_PROCEED, Decision.RETRY_UNSAFE),
        # Approval does not prove that an effect happened or did not happen.
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, True, True, True, False, False), Decision.APPROVED, Decision.RETRY_SAFE),
        # Authority revoked before the approval is also a hard block.
        (Case(Authority.REVOKED, Authority.REVOKED, Approval.VALID, Effect.UNKNOWN, True, True, True, False, True), Decision.BLOCK, Decision.BLOCK),
        # Resource version changes after approval are not silently ignored.
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, True, True, False, True, True), Decision.APPROVED, Decision.BLOCK),
    ]
    for case, expected_initial, expected_recovery in cases:
        assert initial_decision(case) is expected_initial
        assert recovery_decision(case) is expected_recovery
    print(f"FINAL COMPOSITION STRESS {len(cases)}/{len(cases)} PASS")


if __name__ == "__main__":
    main()
