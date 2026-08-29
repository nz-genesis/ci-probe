from conflicting_observations import Causality, Freshness, Observation, State, CONTRACT, PARTIAL, classify


def main() -> None:
    complete = Observation(CONTRACT, "observer-a", Freshness.FRESH, Causality.AFTER)
    partial = Observation(PARTIAL, "observer-b", Freshness.FRESH, Causality.AFTER)
    assert classify((complete, partial)) is State.CONFLICTING

    stale_partial = Observation(PARTIAL, "observer-b", Freshness.STALE, Causality.BEFORE)
    assert classify((complete, stale_partial)) is State.COMPLETE

    stale_complete = Observation(CONTRACT, "observer-a", Freshness.STALE, Causality.BEFORE)
    assert classify((partial, stale_complete)) is State.PARTIAL

    unrelated_complete = Observation(CONTRACT, "observer-a", Freshness.FRESH, Causality.UNRELATED)
    unrelated_partial = Observation(PARTIAL, "observer-b", Freshness.FRESH, Causality.UNRELATED)
    assert classify((unrelated_complete, unrelated_partial)) is State.CONFLICTING

    assert classify(()) is State.UNKNOWN
    print("CONFLICTING OBSERVATIONS REGRESSION 5/5 PASS")


if __name__ == "__main__":
    main()
