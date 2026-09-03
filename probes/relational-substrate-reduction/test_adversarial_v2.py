#!/usr/bin/env python3
"""Domain-neutral adversarial probe for a typed relational representation.

The probe tests decisions and metamorphic invariants, not merely field presence.
No dedicated lifecycle, event, measurement, policy, or constraint object types
are defined.
"""
from dataclasses import dataclass
from typing import Any, Tuple

@dataclass(frozen=True)
class State:
    subject: str
    key: str
    value: Any

@dataclass(frozen=True)
class Capability:
    subject: str
    action: str
    available: bool

@dataclass(frozen=True)
class Authority:
    subject: str
    action: str
    allowed: bool
    valid_from: int
    valid_until: int

@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    claim: str
    target: str
    source: str
    acquired_at: int
    verified: bool

@dataclass(frozen=True)
class Relation:
    kind: str
    left: str
    right: str
    qualifiers: Tuple[Tuple[str, Any], ...] = ()


def q(r: Relation, key: str):
    return dict(r.qualifiers).get(key)


def authorized_at(a: Authority, t: int) -> bool:
    return a.allowed and a.valid_from <= t < a.valid_until


def admissible_start(temp: Any, pressure: Any) -> bool:
    if temp == "unknown" or pressure == "unknown":
        return False
    return temp < 80 and pressure < 10


def effect_once(effects: Tuple[Relation, ...], effect_id: str) -> Tuple[Relation, ...]:
    return effects if any(q(r, "effect_id") == effect_id for r in effects) else effects + (
        Relation("effect", "command", "state", (("effect_id", effect_id),)),
    )


def recovered_health(states: Tuple[State, ...], proof: Evidence) -> bool:
    return proof.verified and proof.claim == "health=healthy" and any(
        s.key == "health" and s.value == "failed" for s in states
    )


def test_concurrent_conflict_is_order_invariant_and_unknown():
    a = Evidence("a", "state=1", "x", "node-a", 10, True)
    b = Evidence("b", "state=2", "x", "node-b", 10, True)
    observations = (a, b)
    reversed_observations = (b, a)
    assert len({e.claim for e in observations}) == 2
    assert sorted(e.claim for e in observations) == sorted(e.claim for e in reversed_observations)
    assert len({e.claim for e in observations}) > 1


def test_delayed_reordering_does_not_change_acquisition_semantics():
    old = Evidence("old", "state=1", "x", "sensor", 5, True)
    new = Evidence("new", "state=2", "x", "sensor", 9, True)
    first = (old, new)
    reordered = (new, old)
    assert sorted(e.acquired_at for e in first) == sorted(e.acquired_at for e in reordered)
    assert max(e.acquired_at for e in first) == 9


def test_duplicate_delivery_is_idempotent():
    once = effect_once((), "e7")
    twice = effect_once(once, "e7")
    assert once == twice
    assert len(twice) == 1


def test_authority_revocation_is_checked_at_effect_boundary():
    granted = Authority("operator", "deploy", True, 0, 10)
    revoked = Authority("operator", "deploy", False, 10, 20)
    assert authorized_at(granted, 9)
    assert not authorized_at(revoked, 12)
    assert not (authorized_at(granted, 9) and authorized_at(revoked, 12))


def test_composed_predicate_fails_closed_on_unknown_component():
    assert admissible_start(75, 5)
    assert not admissible_start(75, "unknown")
    assert not admissible_start("unknown", 5)


def test_acquisition_is_not_verification():
    acquired = Evidence("m1", "temperature=75", "machine", "sensor", 12, False)
    verified = Evidence("m2", "temperature=75", "machine", "sensor", 12, True)
    assert acquired.acquired_at == verified.acquired_at
    assert not acquired.verified and verified.verified


def test_partial_failure_does_not_become_success_without_verified_recovery_proof():
    failed = State("node-a", "health", "failed")
    no_proof = Evidence("p0", "health=healthy", "node-a", "checker", 20, False)
    proof = Evidence("p1", "health=healthy", "node-a", "checker", 21, True)
    assert not recovered_health((failed,), no_proof)
    assert recovered_health((failed,), proof)


def main():
    tests = [
        test_concurrent_conflict_is_order_invariant_and_unknown,
        test_delayed_reordering_does_not_change_acquisition_semantics,
        test_duplicate_delivery_is_idempotent,
        test_authority_revocation_is_checked_at_effect_boundary,
        test_composed_predicate_fails_closed_on_unknown_component,
        test_acquisition_is_not_verification,
        test_partial_failure_does_not_become_success_without_verified_recovery_proof,
    ]
    for test in tests:
        test()
    print(f"ADVERSARIAL_RELATIONAL_SUBSTRATE_V2=PASS ({len(tests)} tests)")

if __name__ == "__main__":
    main()
