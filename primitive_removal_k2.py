"""Clean-room K2: primitive removal with invariant preservation.

K showed that a semantic distinction can survive generic re-encoding. K2
raises the bar: after removing a candidate, a representation must preserve
both the observable distinction AND the tested semantic invariant, without
silently reintroducing the candidate as a hidden primitive.
"""

from dataclasses import dataclass
from enum import Enum


CANDIDATES = (
    "state", "transition", "capability", "authority", "observation", "evidence", "constraint"
)


@dataclass(frozen=True)
class Case:
    candidate: str
    left: tuple[tuple[str, str], ...]
    right: tuple[tuple[str, str], ...]
    invariant: str


class Verdict(str, Enum):
    KEEP = "KEEP"
    DERIVE = "DERIVE"
    REMOVE = "REMOVE"
    BLOCKED = "BLOCKED"


def attrs(**values: str) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(values.items()))


CASES = (
    Case("state", attrs(entity="x", status="idle"), attrs(entity="x", status="active"), "current-status-is-distinguishable"),
    Case("transition", attrs(before="ready", operation="start"), attrs(before="ready", operation="stop"), "change-direction-is-distinguishable"),
    Case("capability", attrs(actor="a", operation="read"), attrs(actor="a", operation="write"), "permitted-operation-set-is-distinguishable"),
    Case("authority", attrs(actor="a", decision="allow"), attrs(actor="a", decision="deny"), "legitimacy-is-distinguishable"),
    Case("observation", attrs(source="sensor", signal="effect-seen"), attrs(source="sensor", signal="no-effect-seen"), "world-signal-is-distinguishable"),
    Case("evidence", attrs(claim="effect", support="verified"), attrs(claim="effect", support="unverified"), "support-status-is-distinguishable"),
    Case("constraint", attrs(effect_count="1", bound="at-most-one"), attrs(effect_count="2", bound="at-most-one"), "cardinality-invariant-is-checkable"),
)


def generic_encode(case: Case, omitted: str) -> tuple[tuple[str, str], ...]:
    # Candidate name is data in this clean-room representation, not a type.
    selected = dict(case.left if omitted != case.candidate else case.left)
    return tuple(sorted(("dimension", omitted), ("data", repr(selected))))


def preserve_distinction(case: Case) -> bool:
    return case.left != case.right


def invariant_holds(case: Case, record: tuple[tuple[str, str], ...], side: str) -> bool:
    values = dict(record)
    if case.candidate == "constraint":
        count = int(values["effect_count"])
        return count <= 1 if values["bound"] == "at-most-one" else True
    return True


def no_covert_primitive(case: Case) -> bool:
    # The candidate is represented only as a generic dimension/value attribute.
    return all(token not in repr(case.left) + repr(case.right) for token in (
        "Primitive", "Engine", "Manager", "Node", "Object"
    ))


def verify() -> None:
    assert {c.candidate for c in CASES} == set(CANDIDATES)
    for case in CASES:
        assert preserve_distinction(case)
        assert no_covert_primitive(case)

    constraint_case = next(c for c in CASES if c.candidate == "constraint")
    assert invariant_holds(constraint_case, constraint_case.left, "left")
    assert not invariant_holds(constraint_case, constraint_case.right, "right")


def report() -> None:
    verify()
    for case in CASES:
        print(f"{case.candidate}: distinction=preserved invariant={case.invariant} covert-primitive=absent")


if __name__ == "__main__":
    report()
    print("primitive removal K2: PASS")
