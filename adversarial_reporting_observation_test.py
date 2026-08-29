from adversarial_reporting_observation import (
    CONTRACT_EFFECTS,
    Case,
    Observation,
    Report,
    Reporter,
    SemanticState,
    classify,
    make_case,
)


def main() -> None:
    honest = make_case(Reporter.HONEST, CONTRACT_EFFECTS)
    false_success = make_case(Reporter.FALSE_SUCCESS, ("A",))
    false_failure = make_case(Reporter.FALSE_FAILURE, CONTRACT_EFFECTS)

    assert classify(honest) is SemanticState.COMPLETE
    assert classify(false_success) is SemanticState.CONFLICTING
    assert classify(false_failure) is SemanticState.CONFLICTING

    without_observer = Case(
        false_success.actual_effects,
        false_success.report,
        None,
        SemanticState.UNKNOWN,
    )
    assert classify(without_observer) is SemanticState.UNKNOWN
    assert classify(false_success, trust_report_only=True) is SemanticState.COMPLETE

    print("ADVERSARIAL REPORTING OBSERVATION REGRESSION 3/3 PASS")


if __name__ == "__main__":
    main()
