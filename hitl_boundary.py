"""Clean-room HITL boundary experiment.

This fixture tests a governance rule, not human cognition: when a proposed
transition crosses an explicit authority, risk, or irreversibility boundary,
a human decision may be required. The requirement is represented as an
ordinary constraint, not as a named HITL primitive.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Proposal:
    name: str
    authorized: bool
    authority_ambiguous: bool
    risk: int
    irreversible: bool


@dataclass(frozen=True)
class GovernanceConstraint:
    human_decision_required: bool


@dataclass(frozen=True)
class Decision:
    admitted: bool
    human_required: bool
    reason: str


RISK_THRESHOLD = 7


def derive_constraint(proposal: Proposal) -> GovernanceConstraint:
    required = (
        proposal.authority_ambiguous
        or proposal.irreversible
        or proposal.risk >= RISK_THRESHOLD
    )
    return GovernanceConstraint(human_decision_required=required)


def evaluate(
    proposal: Proposal,
    constraint: GovernanceConstraint,
    human_decision: bool | None = None,
) -> Decision:
    if not proposal.authorized and not proposal.authority_ambiguous:
        return Decision(False, False, "unauthorized")
    if constraint.human_decision_required:
        if human_decision is None:
            return Decision(False, True, "human-decision-required")
        return Decision(human_decision, True, "human-decision-recorded")
    return Decision(True, False, "within-governance-boundary")


CASES = (
    Proposal("reversible-low-risk", True, False, 2, False),
    Proposal("high-risk-reversible", True, False, 9, False),
    Proposal("irreversible-authorized", True, False, 3, True),
    Proposal("ambiguous-authority", True, True, 2, False),
    Proposal("unauthorized", False, False, 2, False),
)


def verify() -> None:
    low = CASES[0]
    low_decision = evaluate(low, derive_constraint(low))
    assert low_decision.admitted is True
    assert low_decision.human_required is False

    high = CASES[1]
    high_constraint = derive_constraint(high)
    high_pending = evaluate(high, high_constraint)
    assert high_constraint.human_decision_required is True
    assert high_pending.admitted is False
    assert high_pending.human_required is True
    assert evaluate(high, high_constraint, True).admitted is True
    assert evaluate(high, high_constraint, False).admitted is False

    irreversible = CASES[2]
    irreversible_constraint = derive_constraint(irreversible)
    assert irreversible_constraint.human_decision_required is True
    assert evaluate(irreversible, irreversible_constraint).human_required is True

    ambiguous = CASES[3]
    ambiguous_constraint = derive_constraint(ambiguous)
    assert ambiguous_constraint.human_decision_required is True
    assert evaluate(ambiguous, ambiguous_constraint).human_required is True

    unauthorized = CASES[4]
    unauthorized_decision = evaluate(unauthorized, derive_constraint(unauthorized))
    assert unauthorized_decision.admitted is False
    assert unauthorized_decision.human_required is False


def counterfactual_without_boundary() -> Decision:
    proposal = CASES[2]
    unconstrained = GovernanceConstraint(human_decision_required=False)
    return evaluate(proposal, unconstrained)


def verify_removal_counterfactual() -> None:
    constrained = evaluate(CASES[2], derive_constraint(CASES[2]))
    unconstrained = counterfactual_without_boundary()
    assert constrained.admitted is False
    assert constrained.human_required is True
    assert unconstrained.admitted is True


if __name__ == "__main__":
    verify()
    verify_removal_counterfactual()
    print("HITL boundary: PASS")
