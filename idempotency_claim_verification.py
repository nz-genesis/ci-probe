"""Clean-room L6g-R: verify an idempotency claim before using it for retry.

The probe deliberately separates a declared property from evidence supporting
that property. A retry may only be classified safe when the claim is verified,
applicable to the same operation scope/version, fresh enough, and non-conflicting.
Idempotency is not treated as authorization or harmlessness.
"""
from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    UNKNOWN = "unknown"
    RETRY_UNSAFE = "retry_unsafe"
    RETRY_SAFE = "retry_safe"


@dataclass(frozen=True)
class IdempotencyClaim:
    operation_id: str
    resource_id: str
    resource_version: str
    scope: str
    declared_idempotent: bool
    evidence_valid: bool
    evidence_scope: str
    evidence_resource_version: str
    evidence_time: int
    expires_at: int | None = None
    conflicting_evidence: bool = False
    self_attested: bool = False
    harmless: bool = False


def verify_claim(claim: IdempotencyClaim, now: int) -> bool:
    if not claim.declared_idempotent:
        return False
    if not claim.evidence_valid or claim.self_attested:
        return False
    if claim.conflicting_evidence:
        return False
    if claim.evidence_scope != claim.scope:
        return False
    if claim.evidence_resource_version != claim.resource_version:
        return False
    if claim.evidence_time > now:
        return False
    if claim.expires_at is not None and now > claim.expires_at:
        return False
    return True


def retry_decision(claim: IdempotencyClaim, retry_operation_id: str, now: int) -> Decision:
    if retry_operation_id != claim.operation_id:
        return Decision.RETRY_UNSAFE
    if not verify_claim(claim, now):
        return Decision.RETRY_UNSAFE
    return Decision.RETRY_SAFE


def verify() -> None:
    base = dict(
        operation_id="op-1",
        resource_id="R",
        resource_version="v1",
        scope="payment:create:v1",
        declared_idempotent=True,
        evidence_valid=True,
        evidence_scope="payment:create:v1",
        evidence_resource_version="v1",
        evidence_time=10,
        expires_at=20,
    )

    # A verified, applicable, fresh claim can permit same-operation retry.
    assert retry_decision(IdempotencyClaim(**base), "op-1", 15) is Decision.RETRY_SAFE

    # Declaration alone is insufficient.
    unverified = {**base, "evidence_valid": False}
    assert retry_decision(IdempotencyClaim(**unverified), "op-1", 15) is Decision.RETRY_UNSAFE

    # Self-attestation cannot bootstrap verification.
    self_attested = {**base, "self_attested": True}
    assert retry_decision(IdempotencyClaim(**self_attested), "op-1", 15) is Decision.RETRY_UNSAFE

    # Conflicting evidence blocks the safety decision.
    conflicting = {**base, "conflicting_evidence": True}
    assert retry_decision(IdempotencyClaim(**conflicting), "op-1", 15) is Decision.RETRY_UNSAFE

    # Scope mismatch and resource-version drift invalidate applicability.
    scope_mismatch = {**base, "evidence_scope": "payment:refund:v1"}
    assert retry_decision(IdempotencyClaim(**scope_mismatch), "op-1", 15) is Decision.RETRY_UNSAFE
    version_drift = {**base, "resource_version": "v2"}
    assert retry_decision(IdempotencyClaim(**version_drift), "op-1", 15) is Decision.RETRY_UNSAFE

    # Future or expired evidence is not usable at the decision time.
    future = {**base, "evidence_time": 30}
    assert retry_decision(IdempotencyClaim(**future), "op-1", 15) is Decision.RETRY_UNSAFE
    expired = {**base, "expires_at": 14}
    assert retry_decision(IdempotencyClaim(**expired), "op-1", 15) is Decision.RETRY_UNSAFE

    # A different operation identity is never covered by this claim.
    assert retry_decision(IdempotencyClaim(**base), "op-2", 15) is Decision.RETRY_UNSAFE

    # Idempotency does not imply harmlessness or authorization.
    destructive = {**base, "harmless": False}
    assert retry_decision(IdempotencyClaim(**destructive), "op-1", 15) is Decision.RETRY_SAFE


if __name__ == "__main__":
    verify()
    print("IDEMPOTENCY CLAIM VERIFICATION 10/10 PASS")
