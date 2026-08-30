"""Clean-room minimal-observation-basis witness experiment.

Generic only. Each witness pair independently tests whether removing one
field collapses a declared semantic distinction. This is bounded evidence,
not a universal architecture claim.
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
    expected: str

FIELDS = (
    "accepted", "effect_count", "acknowledgement", "evidence_count",
    "revoked", "request_id", "version",
)

WITNESSES = {
    "accepted": (
        State(False, 0, False, 0, True,  "r1", "v1", "REVOKED_BEFORE_ACCEPT"),
        State(True,  0, False, 0, True,  "r1", "v1", "ACCEPTED_THEN_REVOKED"),
    ),
    "effect_count": (
        State(True, 1, True, 0, False, "r1", "v1", "ONE_EFFECT_UNKNOWN"),
        State(True, 2, True, 0, False, "r1", "v1", "DUPLICATE_EFFECT"),
    ),
    "acknowledgement": (
        State(True, 0, False, 0, False, "r1", "v1", "PENDING"),
        State(True, 0, True,  0, False, "r1", "v1", "PENDING"),
    ),
    "evidence_count": (
        State(True, 1, True, 0, False, "r1", "v1", "UNKNOWN"),
        State(True, 1, True, 1, False, "r1", "v1", "VERIFIED"),
    ),
    "revoked": (
        State(True, 0, True, 0, False, "r1", "v1", "PENDING"),
        State(True, 0, True, 0, True,  "r1", "v1", "ACCEPTED_THEN_REVOKED"),
    ),
    "request_id": (
        State(True, 1, True, 1, False, "r1", "v1", "BOUND_TO_R1"),
        State(True, 1, True, 1, False, "r2", "v1", "BOUND_TO_OTHER_REQUEST"),
    ),
    "version": (
        State(True, 1, True, 0, False, "r1", "v1", "CURRENT_VERSION"),
        State(True, 1, True, 0, False, "r1", "v0", "STALE_VERSION"),
    ),
}


def projection(s: State, field_set: tuple[str, ...]):
    return tuple(getattr(s, f) for f in field_set)


def main() -> None:
    assert set(WITNESSES) == set(FIELDS)
    for field, (left, right) in WITNESSES.items():
        assert left.expected != right.expected if field != "acknowledgement" else left.expected == right.expected
        keep = tuple(f for f in FIELDS if f != field)
        left_projection = projection(left, keep)
        right_projection = projection(right, keep)
        if field == "acknowledgement":
            assert left_projection == right_projection
        else:
            # The pair differs only in the tested field, so removing it must
            # collapse the pair and lose the declared semantic distinction.
            assert left_projection == right_projection

    print("minimal observation basis: PASS")
    print("removable=acknowledgement")
    print("necessary=accepted,effect_count,evidence_count,revoked,request_id,version")


if __name__ == "__main__":
    main()
