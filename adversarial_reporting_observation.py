"""Clean-room test for realization/reporting divergence.

A realization mechanism may report a result that disagrees with independently
observable state. The semantic contract is evaluated from admissible evidence,
not from the mechanism's self-report alone. This is generic and contains no
Genesis-specific architecture or data.
"""
from dataclasses import dataclass
from enum import Enum


class Reporter(str, Enum):
    HONEST = "honest"
    FALSE_SUCCESS = "false-success"
    FALSE_FAILURE = "false-failure"


class SemanticState(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNKNOWN = "unknown"
    CONFLICTING = "conflicting"


@dataclass(frozen=True)
class Observation:
    effects: tuple[str, ...]
    source: str


@dataclass(frozen=True)
class Report:
    claimed_state: SemanticState
    source: str


@dataclass(frozen=True)
class Case:
    actual_effects: tuple[str, ...]
    report: Report
    independent_observation: Observation | None
    expected_state: SemanticState


CONTRACT_EFFECTS = ("A", "B")


def classify(case: Case, *, trust_report_only: bool = False) -> SemanticState:
    if trust_report_only:
        return case.report.claimed_state

    if case.independent_observation is None:
        return SemanticState.UNKNOWN

    observed = case.independent_observation.effects
    report = case.report.claimed_state

    if observed == CONTRACT_EFFECTS:
        if report is SemanticState.COMPLETE:
            return SemanticState.COMPLETE
        return SemanticState.CONFLICTING
    if observed == ("A",):
        if report is SemanticState.PARTIAL:
            return SemanticState.PARTIAL
        return SemanticState.CONFLICTING
    return SemanticState.UNKNOWN


def make_case(reporter: Reporter, actual_effects: tuple[str, ...]) -> Case:
    if reporter is Reporter.HONEST:
        claimed = SemanticState.COMPLETE if actual_effects == CONTRACT_EFFECTS else SemanticState.PARTIAL
    elif reporter is Reporter.FALSE_SUCCESS:
        claimed = SemanticState.COMPLETE
    else:
        claimed = SemanticState.PARTIAL
    expected = SemanticState.COMPLETE if actual_effects == CONTRACT_EFFECTS else SemanticState.PARTIAL
    return Case(
        actual_effects,
        Report(claimed, reporter.value),
        Observation(actual_effects, "independent-observer"),
        expected,
    )


def verify() -> None:
    cases = (
        make_case(Reporter.HONEST, ("A", "B")),
        make_case(Reporter.FALSE_SUCCESS, ("A",)),
        make_case(Reporter.FALSE_FAILURE, ("A", "B")),
    )

    assert all(classify(case) is case.expected_state for case in cases[:1])
    assert classify(cases[1]) is SemanticState.CONFLICTING
    assert classify(cases[2]) is SemanticState.CONFLICTING

    # Removing independent observation creates semantic ambiguity rather than a
    # safe success/failure classification.
    assert classify(cases[1], trust_report_only=False) is SemanticState.CONFLICTING
    no_observation = Case(
        cases[1].actual_effects,
        cases[1].report,
        None,
        SemanticState.UNKNOWN,
    )
    assert classify(no_observation) is SemanticState.UNKNOWN

    # Trusting the report alone produces the wrong classification for the
    # deceptive reporter; this is the negative control.
    assert classify(cases[1], trust_report_only=True) is SemanticState.COMPLETE


def main() -> None:
    verify()
    print("ADVERSARIAL REPORTING OBSERVATION 3/3 PASS")


if __name__ == "__main__":
    main()
