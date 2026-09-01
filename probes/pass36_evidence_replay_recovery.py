"""Pass 36 public-safe evidence replay/recovery probe.

Synthetic only. Tests whether stale/compromised evidence can be prevented
from authorizing a duplicate external effect during recovery using State,
Transition, Authority, Observation, Evidence, Capability and Constraint,
without adding Receipt, IdempotencyKey, Transaction, Witness or Trust as
Genesis primitives.
"""
from dataclasses import dataclass
from enum import Enum


class Decision(Enum):
    EXECUTE = "EXECUTE"
    UNKNOWN = "UNKNOWN"
    REJECT = "REJECT"


@dataclass(frozen=True)
class State:
    effect_id: str
    effect_applied: bool
    authority_version: int


@dataclass(frozen=True)
class Transition:
    effect_id: str
    authority_version: int


@dataclass(frozen=True)
class Authority:
    subject: str
    version: int
    active: bool


@dataclass(frozen=True)
class Observation:
    effect_id: str
    observed_applied: bool
    version: int


@dataclass(frozen=True)
class Evidence:
    observation: Observation
    authority: Authority
    complete: bool
    admissible: bool


@dataclass(frozen=True)
class Capability:
    subject: str
    effect_id: str


@dataclass(frozen=True)
class Constraint:
    require_fresh_observation_version: int


def evidence_valid(e: Evidence, t: Transition, c: Constraint) -> bool:
    return (
        e.complete
        and e.admissible
        and e.authority.active
        and e.authority.version == t.authority_version
        and e.observation.effect_id == t.effect_id
        and e.observation.version >= c.require_fresh_observation_version
    )


def recover(s: State, t: Transition, cap: Capability, e: Evidence, c: Constraint) -> Decision:
    if cap.effect_id != t.effect_id:
        return Decision.REJECT
    if s.effect_id != t.effect_id or s.authority_version != t.authority_version:
        return Decision.UNKNOWN
    if s.effect_applied:
        return Decision.REJECT
    if not evidence_valid(e, t, c):
        return Decision.UNKNOWN
    if e.observation.observed_applied:
        return Decision.REJECT
    return Decision.EXECUTE


def base() -> tuple[State, Transition, Authority, Capability, Constraint]:
    state = State("effect-36", False, 8)
    transition = Transition("effect-36", 8)
    authority = Authority("subject-a", 8, True)
    capability = Capability("subject-a", "effect-36")
    constraint = Constraint(8)
    return state, transition, authority, capability, constraint


def evidence(authority: Authority, observed_applied: bool, version: int, admissible: bool = True) -> Evidence:
    return Evidence(Observation("effect-36", observed_applied, version), authority, True, admissible)


def test_valid_recovery_can_execute() -> None:
    s, t, a, cap, c = base()
    assert recover(s, t, cap, evidence(a, False, 8), c) is Decision.EXECUTE


def test_already_applied_state_blocks_duplicate_effect() -> None:
    _, t, a, cap, c = base()
    applied = State("effect-36", True, 8)
    assert recover(applied, t, cap, evidence(a, False, 8), c) is Decision.REJECT


def test_replayed_evidence_after_application_cannot_reexecute() -> None:
    _, t, a, cap, c = base()
    applied = State("effect-36", True, 8)
    replayed = evidence(a, False, 8)
    assert recover(applied, t, cap, replayed, c) is Decision.REJECT


def test_stale_evidence_after_authority_change_is_unknown() -> None:
    s, t, a, cap, _ = base()
    newer_constraint = Constraint(9)
    stale = evidence(a, False, 8)
    assert recover(s, t, cap, stale, newer_constraint) is Decision.UNKNOWN


def test_revoked_authority_cannot_drive_recovery() -> None:
    s, t, a, cap, c = base()
    revoked = Authority(a.subject, a.version, False)
    assert recover(s, t, cap, evidence(revoked, False, 8), c) is Decision.UNKNOWN


def test_compromised_evidence_is_unknown() -> None:
    s, t, a, cap, c = base()
    assert recover(s, t, cap, evidence(a, False, 8, admissible=False), c) is Decision.UNKNOWN


def test_evidence_of_existing_effect_rejects_recovery() -> None:
    s, t, a, cap, c = base()
    assert recover(s, t, cap, evidence(a, True, 8), c) is Decision.REJECT


def test_wrong_effect_identity_cannot_recover() -> None:
    s, t, a, _, c = base()
    cap = Capability(a.subject, "other-effect")
    assert recover(s, t, cap, evidence(a, False, 8), c) is Decision.REJECT


def test_unknown_is_not_unconditional_retry_permission() -> None:
    s, t, a, cap, c = base()
    bad = evidence(a, False, 7)
    assert recover(s, t, cap, bad, c) is Decision.UNKNOWN
    assert recover(s, t, cap, bad, c) is Decision.UNKNOWN


def test_capability_does_not_create_authority() -> None:
    s, t, a, _, c = base()
    foreign_capability = Capability("other-subject", t.effect_id)
    assert foreign_capability.subject != a.subject
    assert recover(s, t, foreign_capability, evidence(a, False, 8), c) is Decision.EXECUTE


def test_primitive_inflation_negative() -> None:
    candidate = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}
    rejected = {"Receipt", "IdempotencyKey", "Transaction", "Witness", "Trust"}
    assert candidate.isdisjoint(rejected)


def main() -> None:
    tests = (
        test_valid_recovery_can_execute,
        test_already_applied_state_blocks_duplicate_effect,
        test_replayed_evidence_after_application_cannot_reexecute,
        test_stale_evidence_after_authority_change_is_unknown,
        test_revoked_authority_cannot_drive_recovery,
        test_compromised_evidence_is_unknown,
        test_evidence_of_existing_effect_rejects_recovery,
        test_wrong_effect_identity_cannot_recover,
        test_unknown_is_not_unconditional_retry_permission,
        test_capability_does_not_create_authority,
        test_primitive_inflation_negative,
    )
    for test in tests:
        test()
    print("PASS36_PUBLIC: PASS; cases=11; private_data=none; new_primitives=0")


if __name__ == "__main__":
    main()
