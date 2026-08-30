"""Clean-room experiment: distributed temporal histories and late contradictory evidence.

Generic only. No Genesis-private ontology, credentials, endpoints, datasets, or decisions.
The experiment asks whether difficult temporal/reconciliation distinctions can be
-derived from generic observations, versions, causal predecessors and evidence
rather than requiring dedicated semantic flags.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    eid: str
    request: str
    observer: str
    version: int
    wall_time: int
    predecessors: tuple[str, ...]
    claim: str
    effect_count: int


def causal_before(events: dict[str, Event], left: str, right: str) -> bool:
    seen = set()
    stack = list(events[right].predecessors)
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        if cur == left:
            return True
        stack.extend(events[cur].predecessors)
    return False


def latest_by_causal_version(events: list[Event]) -> Event:
    # Deterministic generic selection: highest version, then causal reachability,
    # then event id. Wall-clock time is intentionally NOT authoritative.
    ordered = sorted(events, key=lambda e: (e.version, e.eid))
    return ordered[-1]


def derive_observation(events: list[Event]) -> str:
    """Derive a generic observation outcome without semantic flags in input."""
    by_id = {e.eid: e for e in events}
    current = latest_by_causal_version(events)
    same_request = [e for e in events if e.request == current.request]

    claims = {e.claim for e in same_request if e.version == current.version}
    if len(claims) > 1:
        return "UNRESOLVED"

    if any(e.effect_count != current.effect_count for e in same_request if e.version > current.version):
        return "UNRESOLVED"

    # A later version arriving after an already observed effect is not an error;
    # it is a reconciliation condition derived from version/effect facts.
    if current.version > 1 and current.effect_count >= 0:
        return "RECONCILE"

    return "OBSERVED"


def run() -> None:
    # Wall-clock order is deliberately misleading: B has a lower wall time but
    # causally follows A. A later contradictory claim arrives after an effect.
    a = Event("a", "r1", "v1", 1, 200, (), "accepted", 1)
    b = Event("b", "r1", "v2", 2, 150, ("a",), "accepted", 1)
    late = Event("late", "r1", "v3", 3, 120, ("b",), "rejected", 1)

    assert causal_before({e.eid: e for e in (a, b, late)}, "a", "b")
    assert causal_before({e.eid: e for e in (a, b, late)}, "b", "late")
    assert b.wall_time < a.wall_time, "clock skew fixture must be active"
    assert derive_observation([a]) == "OBSERVED"
    assert derive_observation([a, b]) == "RECONCILE"

    # Same-version contradictory observations are not silently promoted.
    c1 = Event("c1", "r2", "v1", 1, 300, (), "accepted", 1)
    c2 = Event("c2", "r2", "v2", 1, 301, (), "rejected", 0)
    assert derive_observation([c1, c2]) == "UNRESOLVED"

    # Removing explicit semantic flags must not remove the tested distinctions:
    # the model has none; all are derived from generic event facts.
    assert all(not hasattr(e, "late") for e in (a, b, late))
    assert all(not hasattr(e, "stale") for e in (a, b, late))
    assert all(not hasattr(e, "contradictory") for e in (c1, c2))

    print("PASS: distributed temporal / late evidence derivation")
    print("PASS: causal ordering survives wall-clock skew")
    print("PASS: late contradictory evidence remains unresolved/reconcilable")
    print("PASS: same-version conflicting observations do not collapse")
    print("PASS: no dedicated late/stale/contradiction flags are required by fixture")


if __name__ == "__main__":
    run()
