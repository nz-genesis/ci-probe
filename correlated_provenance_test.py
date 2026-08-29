from correlated_provenance import Observation, State, classify, naive_observer_majority


def main() -> None:
    cases = (
        (
            (
                Observation(State.COMPLETE, "upstream-1"),
                Observation(State.COMPLETE, "upstream-1"),
                Observation(State.PARTIAL, "observer-3"),
            ),
            State.CONFLICTING,
        ),
        (
            (
                Observation(State.COMPLETE, "observer-1"),
                Observation(State.COMPLETE, "observer-2"),
                Observation(State.PARTIAL, "observer-3"),
            ),
            State.CONFLICTING,
        ),
        (
            tuple(Observation(State.COMPLETE, "same-upstream") for _ in range(3)),
            State.COMPLETE,
        ),
        (
            (
                Observation(State.COMPLETE, "upstream-1", False),
                Observation(State.PARTIAL, "observer-2"),
            ),
            State.PARTIAL,
        ),
        ((), State.UNKNOWN),
    )

    for observations, expected in cases:
        assert classify(observations) is expected

    deceptive = (
        Observation(State.COMPLETE, "upstream-1"),
        Observation(State.COMPLETE, "upstream-1"),
        Observation(State.PARTIAL, "observer-3"),
    )
    assert naive_observer_majority(deceptive) is State.COMPLETE
    assert classify(deceptive) is State.CONFLICTING

    print("CORRELATED PROVENANCE REGRESSION 5/5 PASS")


if __name__ == "__main__":
    main()
