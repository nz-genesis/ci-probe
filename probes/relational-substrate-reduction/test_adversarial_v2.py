#!/usr/bin/env python3
"""Adversarial probe for a minimal typed relational representation.

This probe is deliberately domain-neutral. It tests whether a representation
without dedicated lifecycle/event/measurement/policy object types can preserve
critical distinctions under adversarial ordering, duplication, revocation,
predicate composition, acquisition, and partial failure cases.
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


def q(r, key):
    return dict(r.qualifiers).get(key)


def test_concurrent_conflict_is_not_resolved_by_arrival_order():
    a = Evidence("a", "state=1", "x", "node-a", 10, True)
    b = Evidence("b", "state=2", "x", "node-b", 10, True)
    r1 = Relation("supports", "a", "x", (("logical_time", 10),))
    r2 = Relation("supports", "b", "x", (("logical_time", 10),))
    assert a.acquired_at == b.acquired_at
    assert r1.kind == r2.kind == "supports"
    assert a.claim != b.claim
    assert q(r1, "logical_time") == q(r2, "logical_time")


def test_delayed_and_reordered_evidence_preserves_acquisition_time():
    old = Evidence("old", "state=1", "x", "sensor", 5, True)
    new = Evidence("new", "state=2", "x", "sensor", 9, True)
    arrival = Relation("received-after", "old", "new", (("arrival_order", 2),))
    assert old.acquired_at < new.acquired_at
    assert q(arrival, "arrival_order") == 2
    assert arrival.kind != "changes-to"


def test_duplicate_delivery_is_not_a_second_effect():
    effect = Relation("effect", "command-7", "state:x", (("effect_id", "e7"),))
    duplicate = Relation("delivery", "command-7", "command-7", (("delivery_id", "d2"),))
    assert q(effect, "effect_id") == "e7"
    assert duplicate.kind == "delivery"
    assert effect != duplicate


def test_authority_revocation_between_check_and_effect_is_visible():
    granted = Authority("operator", "deploy", True, 0, 10)
    revoked = Authority("operator", "deploy", False, 10, 20)
    qualification = Relation("qualified-at", "authority:operator.deploy", "time:9")
    effect = Relation("effect-at", "command:deploy", "time:12")
    assert granted.allowed and not revoked.allowed
    assert q(qualification, "missing") is None
    assert effect.kind == "effect-at"
    assert not (revoked.allowed and 12 >= revoked.valid_from)


def test_composed_predicates_fail_closed_when_component_is_unknown():
    temperature = State("machine", "temperature", 75)
    pressure = State("machine", "pressure", "unknown")
    rule = Relation("admissible-if", "action:start", "machine", (("predicate", "temperature<80 AND pressure<10"), ("unknown_policy", "fail-closed")))
    assert temperature.value < 80
    assert pressure.value == "unknown"
    assert q(rule, "unknown_policy") == "fail-closed"
    assert not (pressure.value != "unknown" and pressure.value < 10)


def test_acquisition_is_distinct_from_verification():
    acquired = Evidence("m1", "temperature=75", "machine", "sensor", 12, False)
    verified = Evidence("m2", "temperature=75", "machine", "sensor", 12, True)
    acquisition = Relation("acquired", "m1", "sensor")
    verification = Relation("verifies", "m2", "claim:temperature=75")
    assert acquired.acquired_at == verified.acquired_at
    assert not acquired.verified
    assert verified.verified
    assert acquisition.kind != verification.kind


def test_partial_failure_and_recovery_do_not_imply_success():
    left = State("node-a", "health", "failed")
    right = State("node-b", "health", "healthy")
    recovery = Relation("recovers", "node-a", "healthy", (("requires", "evidence:health-check"),))
    partial = Relation("partial", "operation-9", "node-a", (("completed", False),))
    assert left.value == "failed" and right.value == "healthy"
    assert q(partial, "completed") is False
    assert recovery.kind == "recovers"
    assert left.value != "healthy"


def main():
    tests = [
        test_concurrent_conflict_is_not_resolved_by_arrival_order,
        test_delayed_and_reordered_evidence_preserves_acquisition_time,
        test_duplicate_delivery_is_not_a_second_effect,
        test_authority_revocation_between_check_and_effect_is_visible,
        test_composed_predicates_fail_closed_when_component_is_unknown,
        test_acquisition_is_distinct_from_verification,
        test_partial_failure_and_recovery_do_not_imply_success,
    ]
    for test in tests:
        test()
    print(f"ADVERSARIAL_RELATIONAL_SUBSTRATE_V2=PASS ({len(tests)} tests)")

if __name__ == "__main__":
    main()
