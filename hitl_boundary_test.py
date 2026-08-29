"""Executable checks for the HITL boundary experiment."""

from hitl_boundary import CASES, derive_constraint, evaluate, verify, verify_removal_counterfactual


def test_boundary_invariants() -> None:
    verify()
    verify_removal_counterfactual()


def test_only_material_boundaries_require_human_decision() -> None:
    low = CASES[0]
    assert evaluate(low, derive_constraint(low)).human_required is False

    for proposal in CASES[1:4]:
        assert evaluate(proposal, derive_constraint(proposal)).human_required is True


def test_removing_boundary_constraint_changes_admissibility() -> None:
    proposal = CASES[2]
    constrained = evaluate(proposal, derive_constraint(proposal))
    unconstrained = evaluate(proposal, derive_constraint(CASES[0]))
    assert constrained.admitted is False
    assert unconstrained.admitted is True


if __name__ == "__main__":
    test_boundary_invariants()
    test_only_material_boundaries_require_human_decision()
    test_removing_boundary_constraint_changes_admissibility()
    print("HITL boundary: PASS")
