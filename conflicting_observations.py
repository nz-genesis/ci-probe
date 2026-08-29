"""Clean-room conflicting-observation reduction experiment.

A fixed effect contract is evaluated from independent observations. The
experiment varies freshness and causal relation. It does not choose a winner
when the evidence cannot justify one.
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

    # Evidence that is both fresh and causally after the target boundary is
    # the strongest direct evidence for the post-effect state. Fresh evidence
    # with no causal ordering remains admissible but cannot defeat contradictory
    # evidence. BEFORE evidence cannot refute a later AFTER observation.
    post = tuple(
        o for o in observations
        if o.freshness is Freshness.FRESH and o.causal_relation is Causality.AFTER
    )
    if post:
        states = {State.COMPLETE if o.effects == CONTRACT else State.PARTIAL for o in post}
        if len(states) > 1:
            return State.CONFLICTING
        return next(iter(states))

    fresh_unordered = tuple(
        o for o in observations
        if o.freshness is Freshness.FRESH and o.causal_relation is Causality.UNRELATED
    )
    if fresh_unordered:
        states = {
            State.COMPLETE if o.effects == CONTRACT else State.PARTIAL
            for o in fresh_unordered
        }
        if len(states) > 1:
            return State.CONFLICTING
        return next(iter(states))

    # If only BEFORE evidence exists, it does not establish the post-effect
    # state. Retain uncertainty rather than projecting a pre-effect observation
    # forward in time.
    return State.UNKNOWN


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

    # A fresh BEFORE observation cannot refute a causally later COMPLETE state.
    fresh_before_partial = Observation(PARTIAL, "observer-b", Freshness.FRESH, Causality.BEFORE)
    assert classify((complete, fresh_before_partial)) is State.COMPLETE

    # BEFORE-only evidence cannot establish the post-effect state.
    before_complete = Observation(CONTRACT, "observer-a", Freshness.FRESH, Causality.BEFORE)
    assert classify((before_complete,)) is State.UNKNOWN

    assert classify(()) is State.UNKNOWN

    # Negative control: source name alone cannot resolve fresh conflict.
    assert classify((complete, partial)) is State.CONFLICTING


def main() -> None:
    verify()
    print("CONFLICTING OBSERVATIONS 8/8 PASS")


if __name__ == "__main__":
    main()
