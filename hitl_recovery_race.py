"""Generic clean-room experiment: approval races with authority/effect state."""

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


class Retry(Enum):
    SAFE = "RETRY_SAFE"
    UNSAFE = "RETRY_UNSAFE"
    BLOCK = "BLOCK"


@dataclass(frozen=True)
class Case:
    authority: Authority
    approval: Approval
    effect: Effect
    verified_idempotency: bool
    same_identity: bool
    irreversible: bool


def decide_initial(c: Case) -> str:
    if c.authority is Authority.REVOKED:
        return "BLOCK"
    if c.approval in (Approval.STALE, Approval.CONFLICTING):
        return "BLOCK"
    if c.approval is Approval.NONE:
        return "HITL_REQUIRED" if c.irreversible else "AUTO_PROCEED"
    return "APPROVED"


def decide_retry(c: Case) -> Retry:
    if c.authority is Authority.REVOKED:
        return Retry.BLOCK
    if c.approval is not Approval.VALID:
        return Retry.UNSAFE
    if c.effect in (Effect.PARTIAL, Effect.OBSERVED):
        return Retry.UNSAFE
    if c.effect is Effect.UNKNOWN:
        if c.verified_idempotency and c.same_identity:
            return Retry.SAFE
        return Retry.UNSAFE
    return Retry.UNSAFE


def main() -> None:
    cases = [
        (Case(Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, True, True, True), "APPROVED", Retry.SAFE),
        (Case(Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, False, True, True), "APPROVED", Retry.UNSAFE),
        (Case(Authority.ACTIVE, Approval.VALID, Effect.PARTIAL, True, True, True), "APPROVED", Retry.UNSAFE),
        (Case(Authority.ACTIVE, Approval.VALID, Effect.OBSERVED, True, True, True), "APPROVED", Retry.UNSAFE),
        (Case(Authority.REVOKED, Approval.VALID, Effect.UNKNOWN, True, True, True), "BLOCK", Retry.BLOCK),
        (Case(Authority.ACTIVE, Approval.STALE, Effect.UNKNOWN, True, True, True), "BLOCK", Retry.UNSAFE),
        (Case(Authority.ACTIVE, Approval.CONFLICTING, Effect.UNKNOWN, True, True, True), "BLOCK", Retry.UNSAFE),
        (Case(Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, True, False, True), "APPROVED", Retry.UNSAFE),
        (Case(Authority.ACTIVE, Approval.NONE, Effect.NONE, False, False, True), "HITL_REQUIRED", Retry.UNSAFE),
        (Case(Authority.ACTIVE, Approval.NONE, Effect.NONE, False, False, False), "AUTO_PROCEED", Retry.UNSAFE),
        (Case(Authority.ACTIVE, Approval.VALID, Effect.NONE, True, True, True), "APPROVED", Retry.UNSAFE),
        (Case(Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, True, True, False), "APPROVED", Retry.SAFE),
    ]
    for case, expected_initial, expected_retry in cases:
        assert decide_initial(case) == expected_initial
        assert decide_retry(case) is expected_retry
    print(f"HITL RECOVERY RACE {len(cases)}/{len(cases)} PASS")


if __name__ == "__main__":
    main()
