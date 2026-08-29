"""Clean-room adversarial HITL boundary probe.

Human approval is modeled as scoped decision evidence, not as authority,
execution, or proof of external effect.
"""
from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    AUTO_PROCEED = "auto_proceed"
    HITL_REQUIRED = "hitl_required"
    BLOCK = "block"


class Evidence(str, Enum):
    VERIFIED = "verified"
    UNKNOWN = "unknown"
    CONFLICTING = "conflicting"
    PARTIAL = "partial"


@dataclass(frozen=True)
class Approval:
    operation_id: str
    parameter_fingerprint: str
    resource_version: str
    authority_valid_at_approval: bool
    status: str  # approved, stale, conflicting


@dataclass(frozen=True)
class Scenario:
    operation_id: str
    parameter_fingerprint: str
    resource_version: str
    authority_valid_now: bool
    effect_evidence: Evidence
    irreversible: bool
    harm: str
    reversible: bool
    approval: Approval | None


def decide(s: Scenario) -> Decision:
    if not s.authority_valid_now:
        return Decision.BLOCK
    if s.effect_evidence in {Evidence.CONFLICTING, Evidence.PARTIAL}:
        return Decision.BLOCK
    if s.approval is not None:
        if s.approval.status in {"stale", "conflicting"}:
            return Decision.BLOCK
        if not s.approval.authority_valid_at_approval:
            return Decision.BLOCK
        if s.approval.operation_id != s.operation_id:
            return Decision.BLOCK
        if s.approval.parameter_fingerprint != s.parameter_fingerprint:
            return Decision.BLOCK
        if s.approval.resource_version != s.resource_version:
            return Decision.BLOCK
    if s.effect_evidence is Evidence.UNKNOWN and (s.irreversible or s.harm == "high"):
        return Decision.HITL_REQUIRED
    if s.effect_evidence is Evidence.UNKNOWN:
        return Decision.AUTO_PROCEED if s.reversible and s.harm == "low" else Decision.HITL_REQUIRED
    if s.irreversible or s.harm == "high":
        return Decision.HITL_REQUIRED
    return Decision.AUTO_PROCEED


def verify() -> None:
    good = Approval("op", "p1", "v1", True, "approved")
    stale_params = Approval("op", "p0", "v1", True, "approved")
    stale_version = Approval("op", "p1", "v0", True, "approved")
    stale_time = Approval("op", "p1", "v1", True, "stale")
    revoked_after = Approval("op", "p1", "v1", True, "approved")
    conflicting = Approval("op", "p1", "v1", True, "conflicting")
    invalid_at_approval = Approval("op", "p1", "v1", False, "approved")

    cases = [
        ("matching_approval_low_risk", Scenario("op", "p1", "v1", True, Evidence.VERIFIED, False, "low", True, good), Decision.AUTO_PROCEED),
        ("matching_approval_high_harm", Scenario("op", "p1", "v1", True, Evidence.VERIFIED, False, "high", True, good), Decision.HITL_REQUIRED),
        ("changed_parameters", Scenario("op", "p2", "v1", True, Evidence.VERIFIED, False, "low", True, good), Decision.BLOCK),
        ("changed_resource_version", Scenario("op", "p1", "v2", True, Evidence.VERIFIED, False, "low", True, good), Decision.BLOCK),
        ("stale_time_approval", Scenario("op", "p1", "v1", True, Evidence.VERIFIED, False, "low", True, stale_time), Decision.BLOCK),
        ("revoked_after_approval", Scenario("op", "p1", "v1", False, Evidence.VERIFIED, True, "high", False, revoked_after), Decision.BLOCK),
        ("conflicting_approvals", Scenario("op", "p1", "v1", True, Evidence.CONFLICTING, True, "high", False, conflicting), Decision.BLOCK),
        ("approval_invalid_at_approval", Scenario("op", "p1", "v1", True, Evidence.VERIFIED, True, "high", False, invalid_at_approval), Decision.BLOCK),
        ("unknown_high_harm_without_approval", Scenario("op", "p1", "v1", True, Evidence.UNKNOWN, False, "high", True, None), Decision.HITL_REQUIRED),
        ("unknown_irreversible_without_approval", Scenario("op", "p1", "v1", True, Evidence.UNKNOWN, True, "low", False, None), Decision.HITL_REQUIRED),
        ("unknown_low_reversible", Scenario("op", "p1", "v1", True, Evidence.UNKNOWN, False, "low", True, None), Decision.AUTO_PROCEED),
        ("partial_effect_blocks", Scenario("op", "p1", "v1", True, Evidence.PARTIAL, False, "low", True, good), Decision.BLOCK),
        ("hitl_does_not_create_authority", Scenario("op", "p1", "v1", False, Evidence.UNKNOWN, True, "high", False, good), Decision.BLOCK),
        ("hitl_does_not_verify_effect", Scenario("op", "p1", "v1", True, Evidence.UNKNOWN, True, "high", False, None), Decision.HITL_REQUIRED),
    ]
    for name, scenario, expected in cases:
        actual = decide(scenario)
        assert actual is expected, (name, actual, expected)


if __name__ == "__main__":
    verify()
    print("HITL ADVERSARIAL BOUNDARY 14/14 PASS")
