"""Clean-room primitive-removal counterfactuals.

The experiment distinguishes two questions:
1. Does removing a semantic dimension cause information loss under a fixture?
2. Can the same distinction be represented compositionally without naming the
   candidate as an independent primitive?

A collision under projection is evidence that the *distinction* matters. It is
not, by itself, evidence that the named candidate must be a Genesis primitive.
"""
from dataclasses import dataclass
from enum import Enum
from typing import Any


CANDIDATES = (
    "state", "transition", "capability", "authority", "observation", "evidence", "constraint"
)


@dataclass(frozen=True)
class Record:
    state: str
    transition: str
    capability: str
    authority: str
    observation: str
    evidence: str
    constraint: str

    def as_dict(self) -> dict[str, str]:
        return self.__dict__.copy()


class Verdict(str, Enum):
    DISTINCTION_REQUIRED = "distinction-required"
    COMPOSITIONALLY_REPRESENTABLE = "compositionally-representable"


FIXTURES: dict[str, tuple[Record, Record]] = {
    "state": (
        Record("idle", "none", "none", "none", "none", "none", "none"),
        Record("active", "none", "none", "none", "none", "none", "none"),
    ),
    "transition": (
        Record("ready", "start", "none", "none", "none", "none", "none"),
        Record("ready", "stop", "none", "none", "none", "none", "none"),
    ),
    "capability": (
        Record("ready", "none", "read", "none", "none", "none", "none"),
        Record("ready", "none", "write", "none", "none", "none", "none"),
    ),
    "authority": (
        Record("ready", "write", "write", "allow", "none", "none", "none"),
        Record("ready", "write", "write", "deny", "none", "none", "none"),
    ),
    "observation": (
        Record("active", "start", "none", "none", "none", "effect-seen", "none"),
        Record("active", "start", "none", "none", "none", "no-effect-seen", "none"),
    ),
    "evidence": (
        Record("active", "start", "none", "none", "effect-seen", "verified", "none"),
        Record("active", "start", "none", "none", "effect-seen", "unverified", "none"),
    ),
    "constraint": (
        Record("ready", "start", "write", "allow", "none", "none", "one-effect"),
        Record("ready", "start", "write", "allow", "none", "none", "two-effects"),
    ),
}


def project(record: Record, omitted: str) -> tuple[Any, ...]:
    return tuple(value for key, value in record.as_dict().items() if key != omitted)


def projection_collides(omitted: str) -> bool:
    left, right = FIXTURES[omitted]
    return project(left, omitted) == project(right, omitted)


def composite_reencoding(record: Record, omitted: str) -> tuple[tuple[str, Any], ...]:
    """Encode the omitted distinction as generic data, not as a primitive.

    The representation has one fixed generic shape for every candidate:
    dimension name + dimension value + the remaining record as generic context.
    """
    values = record.as_dict()
    context = tuple(sorted((key, value) for key, value in values.items() if key != omitted))
    return (
        ("dimension", omitted),
        ("value", values[omitted]),
        ("context", context),
    )


def verify() -> None:
    assert set(FIXTURES) == set(CANDIDATES)

    for candidate in CANDIDATES:
        left, right = FIXTURES[candidate]
        assert left.as_dict()[candidate] != right.as_dict()[candidate]
        assert projection_collides(candidate)
        assert composite_reencoding(left, candidate) != composite_reencoding(right, candidate)


def report() -> None:
    verify()
    for candidate in CANDIDATES:
        print(
            f"{candidate}: projection_collision={projection_collides(candidate)} "
            "composite_reencoding=preserves-distinction"
        )


if __name__ == "__main__":
    report()
    print("primitive removal K: PASS")
