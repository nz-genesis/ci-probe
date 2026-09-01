"""Genesis Pass 42: realization-contract change × authority revocation × conflicting observation.

Public-safe synthetic probe. No private Genesis material is used.
"""

from dataclasses import dataclass
from enum import Enum


class Outcome(str, Enum):
    ALLOW = "ALLOW"
    HITL_REQUIRED = "HITL_REQUIRED"
    REJECT = "REJECT"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class Authorization:
    capability: str
    authority: str
    constraint: str
    revoked: bool = False


@dataclass(frozen=True)
class Transition:
    irreversible: bool


@dataclass(frozen=True)
class RealizerContract:
    contract_id: str
    guarantees: frozenset[str]


@dataclass(frozen=True)
class Observation:
    happened: bool


def decide(
    t: Transition,
    auth: Authorization,
    contract: RealizerContract,
    observations: tuple[Observation, ...],
) -> Outcome:
    if not auth.capability or not auth.authority or not auth.constraint:
        return Outcome.REJECT
    if auth.revoked:
        return Outcome.REJECT
    if observations and {o.happened for o in observations} == {True, False}:
        return Outcome.CONFLICT
    if observations and all(o.happened for o in observations):
        return Outcome.REJECT
    if t.irreversible and not {"idempotency", "external_identity", "reconciliation"}.issubset(contract.guarantees):
        return Outcome.HITL_REQUIRED
    return Outcome.ALLOW


def test_contract_downgrade_after_authorization_hits_hitl() -> None:
    t = Transition(True)
    auth = Authorization("cap", "subject", "no-downgrade")
    strong = RealizerContract("strong", frozenset({"idempotency", "external_identity", "reconciliation"}))
    weak = RealizerContract("weak", frozenset())
    assert decide(t, auth, strong, (Observation(False),)) is Outcome.ALLOW
    assert decide(t, auth, weak, (Observation(False),)) is Outcome.HITL_REQUIRED


def test_revocation_cannot_be_bypassed_by_stronger_realizer() -> None:
    t = Transition(True)
    revoked = Authorization("cap", "subject", "constraint", revoked=True)
    strong = RealizerContract("strong", frozenset({"idempotency", "external_identity", "reconciliation"}))
    assert decide(t, revoked, strong, (Observation(False),)) is Outcome.REJECT


def test_conflict_blocks_contract_substitution() -> None:
    t = Transition(True)
    auth = Authorization("cap", "subject", "constraint")
    strong = RealizerContract("strong", frozenset({"idempotency", "external_identity", "reconciliation"}))
    assert decide(t, auth, strong, (Observation(True), Observation(False))) is Outcome.CONFLICT


def test_missing_constraint_fails_closed_before_realizer_choice() -> None:
    t = Transition(False)
    auth = Authorization("cap", "subject", "")
    strong = RealizerContract("strong", frozenset({"idempotency", "external_identity", "reconciliation"}))
    assert decide(t, auth, strong, ()) is Outcome.REJECT


def test_realizer_does_not_create_authority() -> None:
    t = Transition(False)
    auth = Authorization("cap", "subject", "constraint")
    foreign = RealizerContract("subject", frozenset())
    assert decide(t, auth, foreign, ()) is Outcome.ALLOW
    assert auth.authority == "subject"


def test_unknown_is_not_implicit_retry() -> None:
    t = Transition(True)
    auth = Authorization("cap", "subject", "constraint")
    weak = RealizerContract("weak", frozenset())
    assert decide(t, auth, weak, ()) is Outcome.HITL_REQUIRED


def test_removal_no_new_primitive() -> None:
    candidate = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}
    realization_only = {"RealizerContract", "idempotency", "external_identity", "reconciliation"}
    assert realization_only.isdisjoint(candidate)


if __name__ == "__main__":
    tests = [
        test_contract_downgrade_after_authorization_hits_hitl,
        test_revocation_cannot_be_bypassed_by_stronger_realizer,
        test_conflict_blocks_contract_substitution,
        test_missing_constraint_fails_closed_before_realizer_choice,
        test_realizer_does_not_create_authority,
        test_unknown_is_not_implicit_retry,
        test_removal_no_new_primitive,
    ]
    for test in tests:
        test()
    print(f"PASS42_PUBLIC: PASS; cases={len(tests)}")
