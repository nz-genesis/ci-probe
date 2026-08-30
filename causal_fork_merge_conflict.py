"""Clean-room probe: causal fork/merge histories with concurrent conflict.

Generic only. The model derives conflict/reconciliation from a causal DAG,
version, claim and effect observations; no explicit conflict/merge/stale flags
are present in the input.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    eid: str
    request: str
    version: int
    wall_time: int
    predecessors: tuple[str, ...]
    claim: str
    effect_count: int


def ancestors(events: dict[str, Event], eid: str) -> set[str]:
    seen = set()
    stack = list(events[eid].predecessors)
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        stack.extend(events[cur].predecessors)
    return seen


def derive_merge(events: list[Event]) -> str:
    by_id = {e.eid: e for e in events}
    merge = max(events, key=lambda e: (len(e.predecessors), e.version, e.eid))
    branches = [by_id[p] for p in merge.predecessors]
    if len(branches) < 2:
        return "OBSERVED"
    if len({b.claim for b in branches}) > 1:
        return "UNRESOLVED"
    if len({b.effect_count for b in branches}) > 1:
        return "UNRESOLVED"
    return "RECONCILE"


def run() -> None:
    root = Event("root", "r1", 1, 500, (), "accepted", 1)
    a = Event("a", "r1", 2, 600, ("root",), "accepted", 1)
    b = Event("b", "r1", 2, 550, ("root",), "accepted", 1)
    merge = Event("m", "r1", 3, 520, ("a", "b"), "accepted", 1)
    history = {e.eid: e for e in (root, a, b, merge)}

    assert "root" in ancestors(history, "m")
    assert a.wall_time > b.wall_time > merge.wall_time
    assert derive_merge([root, a, b, merge]) == "RECONCILE"

    # Same causal fork, but concurrent branches disagree on claim/effect.
    c = Event("c", "r2", 2, 700, ("root",), "accepted", 1)
    d = Event("d", "r2", 2, 650, ("root",), "rejected", 0)
    bad_merge = Event("bm", "r2", 3, 620, ("c", "d"), "accepted", 1)
    assert derive_merge([root, c, d, bad_merge]) == "UNRESOLVED"

    # No explicit semantic flags are accepted by the representation.
    for e in (root, a, b, merge, c, d, bad_merge):
        assert not hasattr(e, "conflict")
        assert not hasattr(e, "merge_state")
        assert not hasattr(e, "stale")

    print("PASS: causal fork/merge is derived from generic predecessors")
    print("PASS: wall-clock skew does not determine causal order")
    print("PASS: concurrent conflicting branches remain unresolved")
    print("PASS: no dedicated conflict/merge/stale flag is required")


if __name__ == "__main__":
    run()
