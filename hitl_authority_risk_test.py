"""Regression suite for the clean-room HITL boundary probe."""
from hitl_authority_risk import Decision, Evidence, Scenario, decide


def test_unknown_high_harm_requires_hitl():
    assert decide(Scenario(True, Evidence.UNKNOWN, False, "high", True)) is Decision.HITL_REQUIRED


def test_unknown_irreversible_requires_hitl():
    assert decide(Scenario(True, Evidence.UNKNOWN, True, "low", False)) is Decision.HITL_REQUIRED


def test_unknown_low_reversible_can_proceed():
    assert decide(Scenario(True, Evidence.UNKNOWN, False, "low", True)) is Decision.AUTO_PROCEED


def test_revoked_authority_blocks_even_with_verified_evidence():
    assert decide(Scenario(False, Evidence.VERIFIED, True, "high", False)) is Decision.BLOCK


def test_conflict_blocks():
    assert decide(Scenario(True, Evidence.CONFLICTING, False, "low", True)) is Decision.BLOCK


def test_verified_high_harm_requires_hitl():
    assert decide(Scenario(True, Evidence.VERIFIED, False, "high", True)) is Decision.HITL_REQUIRED


def test_verified_low_reversible_can_proceed():
    assert decide(Scenario(True, Evidence.VERIFIED, False, "low", True)) is Decision.AUTO_PROCEED


def test_hitl_does_not_grant_authority():
    assert decide(Scenario(False, Evidence.UNKNOWN, True, "high", False)) is Decision.BLOCK


def test_hitl_does_not_verify_effect():
    assert decide(Scenario(True, Evidence.UNKNOWN, True, "high", False)) is Decision.HITL_REQUIRED


def test_high_harm_is_not_equivalent_to_irreversibility():
    assert decide(Scenario(True, Evidence.VERIFIED, False, "high", True)) is Decision.HITL_REQUIRED


def test_low_harm_irreversibility_still_requires_hitl():
    assert decide(Scenario(True, Evidence.VERIFIED, True, "low", False)) is Decision.HITL_REQUIRED


def test_conflicting_evidence_is_not_escalation_only():
    assert decide(Scenario(True, Evidence.CONFLICTING, True, "high", False)) is Decision.BLOCK


if __name__ == "__main__":
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for test in tests:
        test()
    print("HITL AUTHORITY RISK REGRESSION 12/12 PASS")
