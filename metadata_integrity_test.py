from metadata_integrity import Causality, Freshness, Observation, State, CONTRACT, PARTIAL, classify


def main() -> None:
    complete = Observation(CONTRACT, Freshness.FRESH, Causality.AFTER, True)
    partial = Observation(PARTIAL, Freshness.FRESH, Causality.AFTER, True)
    assert classify((complete, partial)) is State.CONFLICTING

    corrupt_partial = Observation(PARTIAL, Freshness.FRESH, Causality.AFTER, False)
    corrupt_complete = Observation(CONTRACT, Freshness.FRESH, Causality.AFTER, False)
    assert classify((complete, corrupt_partial)) is State.COMPLETE
    assert classify((partial, corrupt_complete)) is State.PARTIAL
    assert classify((corrupt_partial, corrupt_complete)) is State.UNKNOWN

    before = Observation(PARTIAL, Freshness.FRESH, Causality.BEFORE, True)
    corrupt_before = Observation(CONTRACT, Freshness.FRESH, Causality.BEFORE, False)
    assert classify((before,)) is State.UNKNOWN
    assert classify((before, corrupt_before)) is State.UNKNOWN

    u1 = Observation(CONTRACT, Freshness.FRESH, Causality.UNRELATED, True)
    u2 = Observation(PARTIAL, Freshness.FRESH, Causality.UNRELATED, True)
    assert classify((u1, u2)) is State.CONFLICTING
    print("METADATA INTEGRITY REGRESSION 7/7 PASS")


if __name__ == "__main__":
    main()
