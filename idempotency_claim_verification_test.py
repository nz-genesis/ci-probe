"""Regression suite for L6g-R claim verification."""
from idempotency_claim_verification import Decision, IdempotencyClaim, retry_decision, verify


def test_baseline_verification() -> None:
    verify()


def test_unverified_claim_never_becomes_safe() -> None:
    claim = IdempotencyClaim(
        operation_id="op-r",
        resource_id="R",
        resource_version="v1",
        scope="write:v1",
        declared_idempotent=True,
        evidence_valid=False,
        evidence_scope="write:v1",
        evidence_resource_version="v1",
        evidence_time=1,
    )
    assert retry_decision(claim, "op-r", 2) is Decision.RETRY_UNSAFE


def test_idempotency_is_not_harmlessness() -> None:
    claim = IdempotencyClaim(
        operation_id="op-r",
        resource_id="R",
        resource_version="v1",
        scope="destructive:v1",
        declared_idempotent=True,
        evidence_valid=True,
        evidence_scope="destructive:v1",
        evidence_resource_version="v1",
        evidence_time=1,
        harmless=False,
    )
    assert retry_decision(claim, "op-r", 2) is Decision.RETRY_SAFE


if __name__ == "__main__":
    test_baseline_verification()
    test_unverified_claim_never_becomes_safe()
    test_idempotency_is_not_harmlessness()
    print("IDEMPOTENCY CLAIM REGRESSION 3/3 PASS")
