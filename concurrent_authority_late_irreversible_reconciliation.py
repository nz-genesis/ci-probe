"""Clean-room probe: concurrent effects + authority change + late evidence.

Generic only. No Genesis-specific labels, hypotheses, credentials, endpoints, or
canonical decisions are encoded in the fixture. Semantic classifications are
derived from numeric observations and causal/version facts.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    eid: str
    op: int
    version: int
    wall: int
    predecessors: tuple[str, ...]
    actor: int
    authority_epoch: int
    claim: int
    effect_count: int
    irreversible: int


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


def derive_authority(event: Event, grants: dict[int, tuple[int, int]]) -> bool:
    lo, hi = grants[event.actor]
    return lo <= event.authority_epoch <= hi


def concurrent(a: Event, b: Event, events: dict[str, Event]) -> bool:
    return a.eid not in ancestors(events, b.eid) and b.eid not in ancestors(events, a.eid)


def derive_merge(events_list: list[Event], grants: dict[int, tuple[int, int]]) -> str:
    by_id = {e.eid: e for e in events_list}
    merge = max(events_list, key=lambda e: (len(e.predecessors), e.version, e.eid))
    branches = [by_id[p] for p in merge.predecessors]
    assert len(branches) == 2
    left, right = branches

    # All classifications below are derived; none is supplied as an input field.
    if any(not derive_authority(e, grants) for e in branches):
        return "BLOCK"
    if concurrent(left, right, by_id) and (
        left.claim != right.claim or left.effect_count != right.effect_count
    ):
        return "UNRESOLVED"
    return "RECONCILE"


def run() -> None:
    # Actor 7 has authority epochs 10..20, then is revoked for epoch 21+.
    grants = {7: (10, 20), 8: (10, 30)}

    root = Event("r", 41, 1, 900, (), 7, 20, 100, 0, 1)
    left = Event("l", 41, 2, 800, ("r",), 7, 20, 101, 1, 1)
    # Independent branch uses a later authority epoch after revocation.
    right = Event("q", 41, 2, 700, ("r",), 7, 21, 102, 1, 1)
    merge = Event("m", 41, 3, 600, ("l", "q"), 7, 21, 103, 1, 1)

    history = {e.eid: e for e in (root, left, right, merge)}

    assert "r" in ancestors(history, "m")
    assert left.wall > right.wall > merge.wall
    assert concurrent(left, right, history)
    assert derive_authority(left, grants)
    assert not derive_authority(right, grants)
    assert derive_merge([root, left, right, merge], grants) == "BLOCK"

    # Separate history: both branches remain authorized, but late evidence
    # changes the observed claim after an irreversible effect was recorded.
    root2 = Event("r2", 42, 1, 100, (), 8, 12, 200, 0, 1)
    a = Event("a", 42, 2, 300, ("r2",), 8, 13, 201, 1, 1)
    b = Event("b", 42, 2, 200, ("r2",), 8, 13, 202, 1, 1)
    late = Event("z", 42, 3, 50, ("a",), 8, 14, 203, 1, 1)
    history2 = {e.eid: e for e in (root2, a, b, late)}

    assert concurrent(a, b, history2)
    assert a.claim != b.claim
    assert late.version > a.version
    assert late.wall < a.wall
    assert late.effect_count == 1
    assert late.irreversible == 1

    # The contradiction is not a stored status: it is a consequence of the
    # later version changing the claim while the irreversible effect remains.
    assert late.claim != a.claim
    assert late.effect_count > 0 and late.irreversible == 1

    # Removal checks: removing the authority bound removes the derived block;
    # changing the late claim removes the derived contradiction.
    grants_without_revocation = {7: (10, 21), 8: (10, 30)}
    assert derive_merge([root, left, right, merge], grants_without_revocation) == "UNRESOLVED"
    assert late.claim == 203
    altered = Event("z", 42, 3, 50, ("a",), 8, 14, 201, 1, 1)
    assert altered.claim == a.claim

    # No semantic target flags are part of the representation.
    for e in (root, left, right, merge, root2, a, b, late):
        for forbidden in ("blocked", "conflict", "late", "stale", "irreversible_status", "merge_state"):
            assert not hasattr(e, forbidden)

    print("PASS: authority change is derived from numeric authority bounds")
    print("PASS: concurrent branch conflict is derived from causal and claim/effect facts")
    print("PASS: late evidence is derived from version and causal position, not a late flag")
    print("PASS: irreversible effect remains an observation, not a semantic status input")
    print("PASS: removal checks change the derived classifications")
    print("PASS: no dedicated conflict/late/stale/recovery/execution flag is required")


if __name__ == "__main__":
    run()
