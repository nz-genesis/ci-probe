"""Clean-room experiment: correlated evidence must not become authority by count.

The experiment deliberately separates observer count from provenance groups. Two
reports that share one upstream failure origin are not two independent pieces
of evidence. No product architecture or Genesis-specific terminology is used.
"""
from dataclasses import dataclass
from enum import Enum


class State(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNKNOWN = "unknown"
    CONFLICTING = "conflicting"


@dataclass(frozen=True)
class Observation:
    state: State
    provenance_group: str
    metadata_valid: bool = True


def classify(observations: tuple[Observation, ...]) -> State:
    usable = tuple(o for o in observations if o.metadata_valid)
    if not usable:
        return State.UNKNOWN

    by_group: dict[str, set[State]] = {}
    for o in usable:
        by_group.setdefault(o.provenance_group, set()).add(o.state)

    # Contradictory claims from the same provenance group do not establish a
    # winner; the upstream correlation makes observer count non-independent.
    if any(len(states) > 1 for states in by_group.values()):
        return State.CONFLICTING

    group_states = {next(iter(states)) for states in by_group.values()}
    if len(group_states) == 1:
        return next(iter(group_states))

    # No authority or decision policy is assumed. Multiple independent groups
    # disagreeing is preserved as conflict rather than resolved by majority.
    return State.CONFLICTING


def naive_observer_majority(observations: tuple[Observation, ...]) -> State:
    usable = tuple(o for o in observations if o.metadata_valid)
    counts = {s: sum(o.state is s for o in usable) for s in State}
    best = max(counts.values(), default=0)
    winners = [s for s, n in counts.items() if n == best and n > 0]
    return winners[0] if len(winners) == 1 else State.UNKNOWN


def verify() -> None:
    # Three reports do not create three independent votes: A and B share one
    # upstream origin, while C is independent and disagrees.
    correlated_majority = (
        Observation(State.COMPLETE, "upstream-1"),
        Observation(State.COMPLETE, "upstream-1"),
        Observation(State.PARTIAL, "observer-3"),
    )
    assert naive_observer_majority(correlated_majority) is State.COMPLETE
    assert classify(correlated_majority) is State.CONFLICTING

    # Equal observer counts are also insufficient: without an adjudication
    # policy, disagreement between independent provenance groups remains open.
    independent_disagreement = (
        Observation(State.COMPLETE, "observer-1"),
        Observation(State.COMPLETE, "observer-2"),
        Observation(State.PARTIAL, "observer-3"),
    )
    assert classify(independent_disagreement) is State.CONFLICTING

    # A single correlated source cannot manufacture certainty by duplication.
    duplicated = tuple(Observation(State.COMPLETE, "same-upstream") for _ in range(3))
    assert classify(duplicated) is State.COMPLETE
    # This is epistemically limited: the result is only what that one provenance
    # group reports; the experiment deliberately does not call it world truth.

    # Invalid provenance metadata is excluded from resolution.
    invalid = (
        Observation(State.COMPLETE, "upstream-1", False),
        Observation(State.PARTIAL, "observer-2", True),
    )
    assert classify(invalid) is State.PARTIAL

    assert classify(()) is State.UNKNOWN


def main() -> None:
    verify()
    print("CORRELATED PROVENANCE 5/5 PASS")


if __name__ == "__main__":
    main()
