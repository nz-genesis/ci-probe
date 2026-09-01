"""Genesis Pass 41: realization-contract substitution must not silently change authority.

Public-safe synthetic probe. It models two realizers for the same authorized transition.
"""

from dataclasses import dataclass
from enum import Enum


class Outcome(str, Enum):
    ALLOW = "ALLOW"
    HITL_REQUIRED = "HITL_REQUIRED"
    REJECT = "REJECT"


@dataclass(frozen=True)
class Transition:
    id: str
    irreversible: bool


@dataclass(frozen=True)
class Authorization:
    capability: str
    authority: str
    constraint: str


@dataclass(frozen=True)
class Realizer:
    name: str
    idempotent: bool
    external_identity_enforced: bool
    supports_reconciliation: bool


def admission(t: Transition, auth: Authorization, r: Realizer) -> Outcome:
    # The realizer cannot manufacture authority. It can only satisfy or fail the
    # execution guarantees required by the existing authorization/constraint.
    if not auth.capability or not auth.authority or not auth.constraint:
        return Outcome.REJECT
    if t.irreversible and not (
        r.idempotent and r.external_identity_enforced and r.supports_reconciliation
    ):
        return Outcome.HITL_REQUIRED
    return Outcome.ALLOW


def test_same_authorization_different_realizers() -> None:
    t = Transition("T41", irreversible=True)
    auth = Authorization("cap-A", "subject-A", "constraint-A")
    strong = Realizer("strong", True, True, True)
    weak = Realizer("weak", False, False, False)
    assert admission(t, auth, strong) is Outcome.ALLOW
    assert admission(t, auth, weak) is Outcome.HITL_REQUIRED


def test_realizer_substitution_does_not_change_authority() -> None:
    t = Transition("T42", irreversible=False)
    auth = Authorization("cap-A", "subject-A", "constraint-A")
    a = Realizer("A", True, True, True)
    b = Realizer("B", True, True, True)
    assert admission(t, auth, a) is Outcome.ALLOW
    assert admission(t, auth, b) is Outcome.ALLOW
    # Neither realizer changes auth.authority or auth.capability.
    assert auth.authority == "subject-A"
    assert auth.capability == "cap-A"


def test_weak_realizer_cannot_silently_downgrade_safety() -> None:
    t = Transition("T43", irreversible=True)
    auth = Authorization("cap-A", "subject-A", "constraint-no-downgrade")
    weak = Realizer("weak", True, False, True)
    assert admission(t, auth, weak) is Outcome.HITL_REQUIRED


def test_missing_authority_fails_closed() -> None:
    t = Transition("T44", irreversible=False)
    auth = Authorization("cap-A", "", "constraint-A")
    strong = Realizer("strong", True, True, True)
    assert admission(t, auth, strong) is Outcome.REJECT


def test_missing_constraint_fails_closed() -> None:
    t = Transition("T45", irreversible=False)
    auth = Authorization("cap-A", "subject-A", "")
    strong = Realizer("strong", True, True, True)
    assert admission(t, auth, strong) is Outcome.REJECT


def test_realizer_capability_is_not_genesis_authority() -> None:
    t = Transition("T46", irreversible=False)
    auth = Authorization("cap-genesis", "subject-A", "constraint-A")
    foreign = Realizer("foreign", True, True, True)
    assert admission(t, auth, foreign) is Outcome.ALLOW
    # The realizer's name is not an authority subject.
    assert auth.authority == "subject-A"


def test_removal_no_new_primitive() -> None:
    candidate = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}
    realization_fields = {"idempotent", "external_identity_enforced", "supports_reconciliation"}
    assert "Realizer" not in candidate
    assert realization_fields.isdisjoint(candidate)


if __name__ == "__main__":
    tests = [
        test_same_authorization_different_realizers,
        test_realizer_substitution_does_not_change_authority,
        test_weak_realizer_cannot_silently_downgrade_safety,
        test_missing_authority_fails_closed,
        test_missing_constraint_fails_closed,
        test_realizer_capability_is_not_genesis_authority,
        test_removal_no_new_primitive,
    ]
    for test in tests:
        test()
    print(f"PASS41_PUBLIC: PASS; cases={len(tests)}")
