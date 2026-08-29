"""Clean-room experiment: an independence claim is not independence evidence.

The experiment separates a source's declared provenance from whether that
provenance claim is independently attested. No Genesis-specific terminology
or architecture is used.
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
    declared_group: str
    provenance_attested: bool = True


def classify(observations: tuple[Observation, ...]) -> State:
    usable = tuple(o for o in observations if o.provenance_attested)
    unverifiable = tuple(o for o in observations if not o.provenance_attested)

    if not usable:
        return State.UNKNOWN

    groups: dict[str, set[State]] = {}
    for o in usable:
        groups.setdefault(o.declared_group, set()).add(o.state)

    if any(len(states) > 1 for states in groups.values()):
        return State.CONFLICTING

    verified_states = {next(iter(states)) for states in groups.values()}
    if len(verified_states) > 1:
        return State.CONFLICTING

    # An unverified independence claim cannot safely strengthen certainty or
    # establish a provenance split. Preserve uncertainty instead of laundering
    # the source's own claim into authority.
    if unverifiable:
        return State.UNKNOWN

    return next(iter(verified_states))


def naive_declared_majority(observations: tuple[Observation, ...]) -> State:
    counts = {s: sum(o.state is s for o in observations) for s in State}
    best = max(counts.values(), default=0)
    winners = [s for s, n in counts.items() if n == best and n > 0]
    return winners[0] if len(winners) == 1 else State.UNKNOWN


def verify() -> None:
    # Negative control: two sources claim distinct independence but both are
    # actually downstream of the same hidden failure. Their claims are not
    # independently attested, so a majority must not manufacture certainty.
    false_independence = (
        Observation(State.COMPLETE, "claimed-upstream-a", False),
        Observation(State.COMPLETE, "claimed-upstream-b", False),
        Observation(State.PARTIAL, "verified-observer", True),
    )
    assert naive_declared_majority(false_independence) is State.COMPLETE
    assert classify(false_independence) is State.UNKNOWN

    # Verified independent provenance with incompatible states remains an
    # explicit conflict; no hidden adjudication is introduced.
    verified_conflict = (
        Observation(State.COMPLETE, "verified-a", True),
        Observation(State.PARTIAL, "verified-b", True),
    )
    assert classify(verified_conflict) is State.CONFLICTING

    # One verified group plus an unverifiable contradictory claim cannot safely
    # resolve the effect state.
    unverifiable_contradiction = (
        Observation(State.COMPLETE, "verified-a", True),
        Observation(State.PARTIAL, "claimed-b", False),
    )
    assert classify(unverifiable_contradiction) is State.UNKNOWN

    # A single verified, internally consistent provenance group remains only
    # internally consistent evidence; the experiment does not call it world
    # truth.
    single_verified_group = (
        Observation(State.COMPLETE, "verified-a", True),
        Observation(State.COMPLETE, "verified-a", True),
    )
    assert classify(single_verified_group) is State.COMPLETE

    assert classify(()) is State.UNKNOWN


if __name__ == "__main__":
    verify()
    print("ADVERSARIAL PROVENANCE CLAIMS 5/5 PASS")
