"""Clean-room metadata-integrity reduction experiment.

Observation metadata (freshness/causal relation) may itself be unreliable. When
metadata needed to resolve competing evidence is invalid, the probe preserves
uncertainty instead of manufacturing a winner. No trusted resolver or product
architecture is assumed.
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
    freshness: Freshness
    causal_relation: Causality
    metadata_valid: bool


CONTRACT = ("A", "B")
PARTIAL = ("A",)


def state_of(o: Observation) -> State:
    return State.COMPLETE if o.effects == CONTRACT else State.PARTIAL


def classify(observations: tuple[Observation, ...]) -> State:
    if not observations:
        return State.UNKNOWN

    # Invalid metadata cannot safely participate in temporal resolution.
    usable = tuple(o for o in observations if o.metadata_valid)
    if not usable:
        return State.UNKNOWN

    post = tuple(
        o for o in usable
        if o.freshness is Freshness.FRESH and o.causal_relation is Causality.AFTER
    )
    if post:
        states = {state_of(o) for o in post}
        return next(iter(states)) if len(states) == 1 else State.CONFLICTING

    unordered = tuple(
        o for o in usable
        if o.freshness is Freshness.FRESH and o.causal_relation is Causality.UNRELATED
    )
    if unordered:
        states = {state_of(o) for o in unordered}
        return next(iter(states)) if len(states) == 1 else State.CONFLICTING

    return State.UNKNOWN


def verify() -> None:
    complete = Observation(CONTRACT, Freshness.FRESH, Causality.AFTER, True)
    partial = Observation(PARTIAL, Freshness.FRESH, Causality.AFTER, True)
    assert classify((complete, partial)) is State.CONFLICTING

    # Corrupt metadata on one observation removes the basis for using it to
    # resolve the other observation; this is not permission to infer success.
    corrupt_partial = Observation(PARTIAL, Freshness.FRESH, Causality.AFTER, False)
    assert classify((complete, corrupt_partial)) is State.COMPLETE

    corrupt_complete = Observation(CONTRACT, Freshness.FRESH, Causality.AFTER, False)
    assert classify((partial, corrupt_complete)) is State.PARTIAL

    # If every observation needed for temporal resolution has invalid metadata,
    # preserve UNKNOWN.
    assert classify((corrupt_partial, corrupt_complete)) is State.UNKNOWN

    before = Observation(PARTIAL, Freshness.FRESH, Causality.BEFORE, True)
    corrupt_before = Observation(CONTRACT, Freshness.FRESH, Causality.BEFORE, False)
    assert classify((before,)) is State.UNKNOWN
    assert classify((before, corrupt_before)) is State.UNKNOWN

    # Unordered valid evidence still yields CONFLICTING when incompatible.
    u1 = Observation(CONTRACT, Freshness.FRESH, Causality.UNRELATED, True)
    u2 = Observation(PARTIAL, Freshness.FRESH, Causality.UNRELATED, True)
    assert classify((u1, u2)) is State.CONFLICTING


def main() -> None:
    verify()
    print("METADATA INTEGRITY 7/7 PASS")


if __name__ == "__main__":
    main()
