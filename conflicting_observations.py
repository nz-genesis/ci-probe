"""Clean-room conflicting-observation reduction experiment.

A fixed effect contract is evaluated from two independent observations. The
experiment varies freshness and causal relation. It deliberately does not
choose a winner when the evidence cannot justify one.
"""
from dataclasses import dataclass
from enum import Enum


class State(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNKNOWN = "unknown"
    CONFLICTING = "conflicting"


class Freshness(str, Enum):
    FRESH = "fresh"
    STALE = "stale"


class Causality(str, Enum):
    BEFORE = "before"
    AFTER = "after"
    UNRELATED = "unrelated"


@dataclass(frozen=True)
class Observation:
    effects: tuple[str, ...]
    source: str
    freshness: Freshness
    causal_relation: Causality


CONTRACT = ("A", "B")
PARTIAL = ("A",)


def classify(observations: tuple[Observation, ...]) -> State:
    if not observations:
        return State.UNKNOWN
    fresh = tuple(o for o in observations if o.freshness is Freshness.FRESH)
    candidates = fresh or observations
    states = {State.COMPLETE if o.effects == CONTRACT else State.PARTIAL for o in candidates}
    if len(states) > 1:
        return State.CONFLICTING
    return next(iter(states))


def verify() -> None:
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

    # Negative control: source name alone cannot resolve fresh conflict.
    assert classify((complete, partial)) is State.CONFLICTING


def main() -> None:
    verify()
    print("CONFLICTING OBSERVATIONS 6/6 PASS")


if __name__ == "__main__":
    main()
