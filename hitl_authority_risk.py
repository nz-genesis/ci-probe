"""Clean-room HITL authority/risk/irreversibility boundary probe."""
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


@dataclass(frozen=True)
class Scenario:
    authority_valid: bool
    evidence: Evidence
    irreversible: bool
    harm: str  # low, high
    reversible: bool


def decide(s: Scenario) -> Decision:
    if not s.authority_valid or s.evidence is Evidence.CONFLICTING:
        return Decision.BLOCK
    if s.evidence is Evidence.UNKNOWN and (s.irreversible or s.harm == "high"):
        return Decision.HITL_REQUIRED
    if s.evidence is Evidence.UNKNOWN:
        return Decision.AUTO_PROCEED if s.reversible and s.harm == "low" else Decision.HITL_REQUIRED
    if s.irreversible or s.harm == "high":
        return Decision.HITL_REQUIRED
    return Decision.AUTO_PROCEED


def verify() -> None:
    cases = [
        ("unknown_low_reversible", Scenario(True, Evidence.UNKNOWN, False, "low", True), Decision.AUTO_PROCEED),
        ("unknown_high_reversible", Scenario(True, Evidence.UNKNOWN, False, "high", True), Decision.HITL_REQUIRED),
        ("unknown_low_irreversible", Scenario(True, Evidence.UNKNOWN, True, "low", False), Decision.HITL_REQUIRED),
        ("unknown_high_irreversible", Scenario(True, Evidence.UNKNOWN, True, "high", False), Decision.HITL_REQUIRED),
        ("verified_low_reversible", Scenario(True, Evidence.VERIFIED, False, "low", True), Decision.AUTO_PROCEED),
        ("verified_high_reversible", Scenario(True, Evidence.VERIFIED, False, "high", True), Decision.HITL_REQUIRED),
        ("verified_low_irreversible", Scenario(True, Evidence.VERIFIED, True, "low", False), Decision.HITL_REQUIRED),
        ("verified_high_irreversible", Scenario(True, Evidence.VERIFIED, True, "high", False), Decision.HITL_REQUIRED),
        ("revoked_unknown", Scenario(False, Evidence.UNKNOWN, False, "low", True), Decision.BLOCK),
        ("revoked_verified", Scenario(False, Evidence.VERIFIED, True, "high", False), Decision.BLOCK),
        ("conflicting_authority", Scenario(True, Evidence.CONFLICTING, True, "high", False), Decision.BLOCK),
        ("conflicting_low", Scenario(True, Evidence.CONFLICTING, False, "low", True), Decision.BLOCK),
    ]
    for name, scenario, expected in cases:
        actual = decide(scenario)
        assert actual is expected, (name, actual, expected)

    # Reduction checks: HITL is a decision boundary, not an execution mechanism.
    assert decide(Scenario(True, Evidence.UNKNOWN, True, "low", False)) is Decision.HITL_REQUIRED
    assert decide(Scenario(True, Evidence.VERIFIED, True, "low", False)) is Decision.HITL_REQUIRED
    assert decide(Scenario(False, Evidence.VERIFIED, False, "low", True)) is Decision.BLOCK
    assert decide(Scenario(True, Evidence.UNKNOWN, False, "low", True)) is Decision.AUTO_PROCEED


if __name__ == "__main__":
    verify()
    print("HITL AUTHORITY RISK VERIFICATION 12/12 PASS")
