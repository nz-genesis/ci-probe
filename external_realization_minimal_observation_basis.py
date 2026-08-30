"""Clean-room minimal-observation-basis experiment.

Generic only. Each witness pair declares a semantic distinction independently
of the projection under test. A field is necessary only for the bounded
witness set; this is not a universal architecture claim.
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

# Every pair differs in exactly one field. The expected labels are the
# semantic distinction being tested, not a classification generated from the
# projected fields. The acknowledgement pair intentionally has the same
# expected label: acknowledgement is tested for removability.
CASES = [
    # accepted is necessary: revoked-before-accept != accepted-then-revoked.
    State(False, 0, False, 0, True,  "r1", "v1", "REVOKED_BEFORE_ACCEPT"),
    State(True,  0, False, 0, True,  "r1", "v1", "ACCEPTED_THEN_REVOKED"),
    # effect_count is necessary: one effect != duplicate effect.
    State(True,  1, True, 0, False, "r1", "v1", "ONE_EFFECT_UNKNOWN"),
    State(True,  2, True, 0, False, "r1", "v1", "DUPLICATE_EFFECT"),
    # acknowledgement is removable for the selected semantic distinctions.
    State(True,  0, False, 0, False, "r1", "v1", "PENDING"),
    State(True,  0, True,  0, False, "r1", "v1", "PENDING"),
    # evidence_count is necessary: possible effect != verified effect.
    State(True,  1, True, 0, False, "r1", "v1", "UNKNOWN"),
    State(True,  1, True, 1, False, "r1", "v1", "VERIFIED"),
    # revoked is necessary: accepted current != accepted then revoked.
    State(True, 0, True, 0, False, "r1", "v1", "PENDING"),
    State(True, 0, True, 0, True,  "r1", "v1", "ACCEPTED_THEN_REVOKED"),
    # request_id is necessary for the selected evidence-binding distinction.
    State(True, 1, True, 1, False, "r1", "v1", "BOUND_TO_R1"),
    State(True, 1, True, 1, False, "r2", "v1", "BOUND_TO_OTHER_REQUEST"),
    # version is necessary for the selected freshness distinction.
    State(True, 1, True, 0, False, "r1", "v1", "CURRENT_VERSION"),
    State(True, 1, True, 0, False, "r1", "v0", "STALE_VERSION"),
]


def projection(s: State, keep: tuple[str, ...]):
    return tuple(getattr(s, f) for f in keep)


def collisions_for(keep: tuple[str, ...]) -> int:
    buckets = {}
    for s in CASES:
        buckets.setdefault(projection(s, keep), set()).add(s.expected)
    return sum(len(labels) - 1 for labels in buckets.values() if len(labels) > 1)


def main() -> None:
    assert collisions_for(FIELDS) == 0

    removable = []
    necessary = []
    for field in FIELDS:
        keep = tuple(f for f in FIELDS if f != field)
        if collisions_for(keep) == 0:
            removable.append(field)
        else:
            necessary.append(field)

    assert removable == ["acknowledgement"]
    assert necessary == [
        "accepted", "effect_count", "evidence_count", "revoked",
        "request_id", "version",
    ]

    print("minimal observation basis: PASS")
    print("removable=acknowledgement")
    print("necessary=accepted,effect_count,evidence_count,revoked,request_id,version")


if __name__ == "__main__":
    main()
