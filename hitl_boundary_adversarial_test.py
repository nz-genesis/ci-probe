"""Regression suite for adversarial HITL boundary semantics."""
from hitl_boundary_adversarial import Decision, Evidence, Approval, Scenario, decide


def test_changed_parameters_block():
    approval = Approval("op", "p1", "v1", True, "approved")
    assert decide(Scenario("op", "p2", "v1", True, Evidence.VERIFIED, False, "low", True, approval)) is Decision.BLOCK


def test_changed_version_blocks():
    approval = Approval("op", "p1", "v1", True, "approved")
    assert decide(Scenario("op", "p1", "v2", True, Evidence.VERIFIED, False, "low", True, approval)) is Decision.BLOCK


def test_stale_approval_blocks():
    approval = Approval("op", "p1", "v1", True, "stale")
    assert decide(Scenario("op", "p1", "v1", True, Evidence.VERIFIED, False, "low", True, approval)) is Decision.BLOCK


def test_revoked_after_approval_blocks():
    approval = Approval("op", "p1", "v1", True, "approved")
    assert decide(Scenario("op", "p1", "v1", False, Evidence.VERIFIED, True, "high", False, approval)) is Decision.BLOCK


def test_conflicting_evidence_blocks():
    approval = Approval("op", "p1", "v1", True, "approved")
    assert decide(Scenario("op", "p1", "v1", True, Evidence.CONFLICTING, True, "high", False, approval)) is Decision.BLOCK


def test_partial_effect_blocks():
    approval = Approval("op", "p1", "v1", True, "approved")
    assert decide(Scenario("op", "p1", "v1", True, Evidence.PARTIAL, False, "low", True, approval)) is Decision.BLOCK


def test_unknown_high_harm_requires_hitl():
    assert decide(Scenario("op", "p1", "v1", True, Evidence.UNKNOWN, False, "high", True, None)) is Decision.HITL_REQUIRED


def test_unknown_irreversible_requires_hitl():
    assert decide(Scenario("op", "p1", "v1", True, Evidence.UNKNOWN, True, "low", False, None)) is Decision.HITL_REQUIRED


def test_low_risk_reversible_can_auto_proceed():
    assert decide(Scenario("op", "p1", "v1", True, Evidence.UNKNOWN, False, "low", True, None)) is Decision.AUTO_PROCEED


def test_verified_high_harm_requires_hitl():
    assert decide(Scenario("op", "p1", "v1", True, Evidence.VERIFIED, False, "high", True, None)) is Decision.HITL_REQUIRED


def test_verified_irreversible_requires_hitl():
    assert decide(Scenario("op", "p1", "v1", True, Evidence.VERIFIED, True, "low", False, None)) is Decision.HITL_REQUIRED


def test_approval_does_not_create_authority():
    approval = Approval("op", "p1", "v1", True, "approved")
    assert decide(Scenario("op", "p1", "v1", False, Evidence.VERIFIED, False, "low", True, approval)) is Decision.BLOCK


def test_approval_invalid_at_approval_blocks():
    approval = Approval("op", "p1", "v1", False, "approved")
    assert decide(Scenario("op", "p1", "v1", True, Evidence.VERIFIED, True, "high", False, approval)) is Decision.BLOCK


def test_conflicting_approval_blocks():
    approval = Approval("op", "p1", "v1", True, "conflicting")
    assert decide(Scenario("op", "p1", "v1", True, Evidence.VERIFIED, False, "low", True, approval)) is Decision.BLOCK


def test_hitl_does_not_verify_effect():
    assert decide(Scenario("op", "p1", "v1", True, Evidence.UNKNOWN, True, "high", False, None)) is Decision.HITL_REQUIRED


def test_stale_parameter_approval_is_not_reused():
    approval = Approval("op", "old", "v1", True, "approved")
    assert decide(Scenario("op", "new", "v1", True, Evidence.UNKNOWN, False, "low", True, approval)) is Decision.BLOCK


if __name__ == "__main__":
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for test in tests:
        test()
    print("HITL ADVERSARIAL REGRESSION 16/16 PASS")
