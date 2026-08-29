"""Clean-room experiment: apparently independent attestations may share a root.

No trust engine is assumed. The model treats an attestation graph as evidence
with provenance edges and refuses certainty when independent-looking claims
collapse onto one common root or form a cycle.
"""
from dataclasses import dataclass
from enum import Enum


class State(str, Enum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    UNKNOWN = "unknown"
    CONFLICTING = "conflicting"


@dataclass(frozen=True)
class Attestation:
    source: str
    state: State
    root: str
    attested: bool = True
    attests: tuple[str, ...] = ()


def classify(attestations: tuple[Attestation, ...]) -> State:
    usable = tuple(a for a in attestations if a.attested)
    if not usable:
        return State.UNKNOWN

    # A cycle means the apparent attestation chain has no independent anchor.
    graph = {a.source: set(a.attests) for a in usable}
    for source, targets in graph.items():
        if source in targets:
            return State.UNKNOWN
        for target in targets:
            if target in graph and source in graph[target]:
                return State.UNKNOWN

    roots = {a.root for a in usable}
    states = {a.state for a in usable}

    # Apparently different sources sharing one root are not independent votes.
    if len(roots) == 1 and len(states) > 1:
        return State.UNKNOWN
    if len(roots) == 1:
        return next(iter(states))

    if len(states) > 1:
        return State.CONFLICTING
    return next(iter(states))


def naive_source_majority(attestations: tuple[Attestation, ...]) -> State:
    counts = {s: sum(a.state is s for a in attestations) for s in State}
    best = max(counts.values(), default=0)
    winners = [s for s, n in counts.items() if n == best and n > 0]
    return winners[0] if len(winners) == 1 else State.UNKNOWN


def verify() -> None:
    common_root = (
        Attestation("a", State.COMPLETE, "root-x"),
        Attestation("b", State.COMPLETE, "root-x"),
        Attestation("c", State.PARTIAL, "root-x"),
    )
    assert naive_source_majority(common_root) is State.COMPLETE
    assert classify(common_root) is State.UNKNOWN

    independent_conflict = (
        Attestation("a", State.COMPLETE, "root-a"),
        Attestation("b", State.PARTIAL, "root-b"),
    )
    assert classify(independent_conflict) is State.CONFLICTING

    circular = (
        Attestation("a", State.COMPLETE, "root-a", True, ("b",)),
        Attestation("b", State.COMPLETE, "root-b", True, ("a",)),
    )
    assert classify(circular) is State.UNKNOWN

    one_root_consistent = (
        Attestation("a", State.COMPLETE, "root-a"),
        Attestation("b", State.COMPLETE, "root-a"),
    )
    assert classify(one_root_consistent) is State.COMPLETE

    assert classify(()) is State.UNKNOWN


if __name__ == "__main__":
    verify()
    print("CIRCULAR COMMON-ROOT ATTESTATION 5/5 PASS")
