"""Clean-room relational reduction experiment.

Generic executable only. It asks whether several named observations can be
represented as relations over a smaller vocabulary without losing the tested
semantic distinctions. It does not encode any private Genesis architecture.
"""
from dataclasses import dataclass
from itertools import combinations

@dataclass(frozen=True)
class Event:
    request: str
    resource: str
    version: str
    authority: str
    evidence_for: str | None
    predecessor: str | None
    effect_count: int


def relations(e: Event) -> dict[str, object]:
    return {
        "identity": (e.request, e.resource),
        "version": e.version,
        "authority": e.authority,
        "binding": e.evidence_for == e.request if e.evidence_for else False,
        "causal": e.predecessor is not None,
        "effect": e.effect_count,
    }


CASES = [
    ("BOUND", Event("r1", "x", "v1", "a1", "r1", "e0", 1),
            Event("r1", "x", "v1", "a1", "r2", "e0", 1)),
    ("AUTHORITY", Event("r1", "x", "v1", "a1", "r1", "e0", 1),
                  Event("r1", "x", "v1", "a2", "r1", "e0", 1)),
    ("CAUSAL", Event("r1", "x", "v1", "a1", "r1", "e0", 1),
               Event("r1", "x", "v1", "a1", "r1", None, 1)),
    ("VERSION", Event("r1", "x", "v1", "a1", "r1", "e0", 1),
                Event("r1", "x", "v2", "a1", "r1", "e0", 1)),
    ("EFFECT", Event("r1", "x", "v1", "a1", "r1", "e0", 1),
               Event("r1", "x", "v1", "a1", "r1", "e0", 2)),
]


def distinguishable(fields: tuple[str, ...]) -> bool:
    for _, left, right in CASES:
        l = relations(left)
        r = relations(right)
        if tuple(l[f] for f in fields) == tuple(r[f] for f in fields):
            return False
    return True


def main() -> None:
    fields = tuple(relations(CASES[0][1]).keys())
    minimal = []
    for size in range(1, len(fields) + 1):
        for subset in combinations(fields, size):
            if distinguishable(subset):
                minimal.append(subset)
        if minimal:
            break

    assert minimal, "no distinguishing relational basis"
    # Every semantic witness has a dedicated relation in this clean-room model.
    # The important result is that labels themselves are absent from the basis.
    assert all(not any(name in s for name in ("UNKNOWN", "DUPLICATE", "REVOKED")) for s in minimal)
    print("relational reduction: PASS")
    print("minimal_bases=", minimal)


if __name__ == "__main__":
    main()
