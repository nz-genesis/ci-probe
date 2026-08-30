"""Clean-room minimal-observation-basis experiment.

Generic only. This asks which observation fields are necessary to preserve
selected external-state distinctions. Necessity is bounded to this matrix;
it is not a universal architecture claim.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class State:
    accepted: bool
    effect_count: int
    acknowledgement: bool
    evidence_count: int
    revoked: bool
    request_id: str
    version: str


def semantic_class(s: State) -> str:
    if s.revoked and not s.accepted:
        return "REVOKED_BEFORE_ACCEPT"
    if s.revoked and s.accepted and s.effect_count == 0:
        return "ACCEPTED_THEN_REVOKED_NO_EFFECT"
    if s.effect_count > 1:
        return "DUPLICATE_EFFECT"
    if s.effect_count == 1 and s.evidence_count == 0:
        return "UNKNOWN_AFTER_POSSIBLE_EFFECT"
    if s.effect_count == 1 and s.evidence_count == 1:
        return "VERIFIED"
    return "PENDING"


FIELDS = (
    "accepted", "effect_count", "acknowledgement", "evidence_count",
    "revoked", "request_id", "version",
)

CASES = [
    State(False, 0, False, 0, True, "r1", "v1"),
    State(True, 0, False, 0, False, "r1", "v1"),
    State(True, 0, True, 0, False, "r1", "v1"),
    State(True, 0, True, 0, True, "r1", "v1"),
    State(True, 1, False, 0, False, "r1", "v1"),
    State(True, 1, True, 1, False, "r1", "v1"),
    State(True, 2, True, 2, False, "r1", "v1"),
    State(True, 1, True, 0, False, "r1", "v0"),
    State(True, 1, True, 0, False, "r2", "v1"),
    State(True, 1, True, 1, False, "r1", "v1"),
    State(True, 1, True, 1, False, "r2", "v1"),
]


def semantic_key(s: State):
    # Cross-request identity and freshness are represented as explicit
    # semantic distinctions for this bounded test matrix.
    base = semantic_class(s)
    if s.effect_count == 1 and s.evidence_count == 1:
        return (base, s.request_id, s.version)
    if s.effect_count == 1 and s.evidence_count == 0:
        return (base, s.version)
    return (base,)


def projection(s: State, keep: tuple[str, ...]):
    return tuple(getattr(s, f) for f in keep)


def collision_count(keep: tuple[str, ...]) -> int:
    buckets = {}
    for s in CASES:
        buckets.setdefault(projection(s, keep), set()).add(semantic_key(s))
    return sum(len(labels) - 1 for labels in buckets.values() if len(labels) > 1)


def main() -> None:
    baseline = tuple(FIELDS)
    assert collision_count(baseline) == 0

    removable = []
    necessary = []
    for field in FIELDS:
        keep = tuple(f for f in FIELDS if f != field)
        if collision_count(keep) == 0:
            removable.append(field)
        else:
            necessary.append(field)

    # Acknowledgement is not part of the selected semantic distinctions: it
    # is an observation channel, while effect/evidence determine the tested
    # external-state classification.
    assert "acknowledgement" in removable
    for field in ("accepted", "effect_count", "evidence_count", "revoked", "request_id", "version"):
        assert field in necessary

    print("minimal observation basis: PASS")
    print("removable=acknowledgement")
    print("necessary=accepted,effect_count,evidence_count,revoked,request_id,version")


if __name__ == "__main__":
    main()
