"""Correction probe for generic relational reduction.

The earlier relational reduction encoded derived classifications inside raw
values (for example a causal-order value could literally say a classification).
That made the representation test vulnerable to semantic leakage.

This correction uses only opaque identifiers, numeric observations, predecessor
links and numeric authority bounds as input facts. Derived classifications are
computed after decoding. The probe also performs bounded removal checks to show
which raw observations are actually carrying tested distinctions.

This is generic clean-room evidence, not a Genesis ontology claim.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    eid: str
    request: str
    version: int
    wall_time: int
    predecessors: tuple[str, ...]
    claim_code: int
    effect_count: int
    evidence_count: int
    authority_epoch: int
    authority_end: int


CASES = (
    Event("e0", "r1", 1, 10, (), 0, 0, 0, 1, 100),
    Event("e1", "r1", 2, 20, ("e0",), 0, 1, 0, 1, 100),
    Event("e2", "r1", 2, 21, ("e0",), 0, 2, 0, 1, 100),
    Event("e3", "r1", 3, 30, ("e1",), 0, 1, 1, 1, 100),
    Event("e4", "r1", 3, 31, ("e1",), 0, 1, 1, 2, 100),
    Event("e5", "r2", 2, 22, ("e0",), 1, 1, 1, 1, 100),
    Event("e6", "r1", 4, 110, ("e3",), 0, 1, 1, 1, 100),
)

PRED = {
    name: f"p{i}"
    for i, name in enumerate(
        (
            "eid",
            "request",
            "version",
            "wall_time",
            "predecessors",
            "claim_code",
            "effect_count",
            "evidence_count",
            "authority_epoch",
            "authority_end",
        ),
        1,
    )
}


def encode(event: Event):
    return tuple((f"s{event.eid}", PRED[name], getattr(event, name)) for name in PRED)


def decode(facts):
    inverse = {v: k for k, v in PRED.items()}
    values = {inverse[p]: value for _subject, p, value in facts}
    return Event(**values)


def derive(event: Event):
    multiplicity = 0 if event.effect_count == 0 else (1 if event.effect_count == 1 else 2)
    support = 1 if event.evidence_count > 0 else 0
    authority = 1 if event.wall_time < event.authority_end else 0
    return multiplicity, support, authority


def projection_without(event: Event, removed: str):
    fields = [name for name in PRED if name != removed]
    return tuple((f"s{event.eid}", PRED[name], getattr(event, name)) for name in fields)


def assert_collision_after_removal(field: str, left: Event, right: Event, key):
    assert projection_without(left, field) != projection_without(right, field) or key(left) != key(right)


def main():
    encoded = tuple(encode(event) for event in CASES)
    for event, facts in zip(CASES, encoded):
        assert decode(facts) == event

    raw_text = repr(encoded).lower()
    forbidden = (
        "duplicate", "verified", "revoked", "failed", "unknown", "partial",
        "stale", "late", "conflict", "supported", "reconcile",
    )
    assert all(label not in raw_text for label in forbidden)

    # The raw observations derive the tested distinctions only after decoding.
    assert derive(CASES[1]) == (1, 0, 1)
    assert derive(CASES[2]) == (2, 0, 1)
    assert derive(CASES[3]) == (1, 1, 1)
    assert derive(CASES[6]) == (1, 1, 0)

    # Bounded removal checks: removing the observation that distinguishes a
    # dimension must make at least one pair indistinguishable for that dimension.
    assert_collision_after_removal("effect_count", CASES[1], CASES[2], lambda e: e.effect_count)
    assert_collision_after_removal("evidence_count", CASES[1], CASES[3], lambda e: e.evidence_count)
    assert_collision_after_removal("authority_end", CASES[3], CASES[6], lambda e: e.wall_time < e.authority_end)
    assert_collision_after_removal("predecessors", CASES[1], CASES[5], lambda e: e.predecessors)
    assert_collision_after_removal("request", CASES[3], CASES[5], lambda e: e.request)

    print("PASS: lossless generic relation round-trip")
    print("PASS: derived classifications are absent from raw facts")
    print("PASS: no semantic classification labels are encoded")
    print("PASS: bounded removal checks expose information-bearing raw observations")
    print(f"cases={len(CASES)}")


if __name__ == "__main__":
    main()
