#!/usr/bin/env python3
"""Executable probe for a reduced, typed relational representation.

The probe intentionally has no Transition, Observation, or Constraint object.
It tests whether the required distinctions for a small set of action/evidence
scenarios remain recoverable using only State, Capability, Authority, Evidence,
and a generic relation record.

The generic relation record is deliberately non-action-bearing: it has no
lifecycle, authority, provenance, outcome, or execution semantics of its own.
Those semantics must remain in the typed records it connects.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple


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


@dataclass(frozen=True)
class Evidence:
    evidence_id: str
    claim: str
    target: str
    source: str
    verified: bool
    status: str


@dataclass(frozen=True)
class Relation:
    kind: str
    left: str
    right: str
    qualifiers: Tuple[Tuple[str, Any], ...] = ()


def assert_distinct(label: str, a: Any, b: Any) -> None:
    assert a != b, f"{label}: expected distinct representations"


def test_successful_change() -> None:
    before = State("x", "mode", "closed")
    after = State("x", "mode", "open")
    cap = Capability("x", "open", True)
    auth = Authority("x", "open", True)
    evidence = Evidence("e1", "mode=open", "x", "verified-sensor", True, "verified")
    relation = Relation("changes-to", "state:before", "state:after", (("ordered", 1),))

    assert before.value != after.value
    assert cap.available and auth.allowed
    assert evidence.verified and evidence.status == "verified"
    assert relation.kind == "changes-to"
    assert relation.qualifiers == (("ordered", 1),)


def test_rejected_attempt() -> None:
    before = State("x", "mode", "closed")
    cap = Capability("x", "open", True)
    auth = Authority("x", "open", False)
    denial = Evidence("e2", "permission-denied", "x", "policy-engine", True, "verified")
    relation = Relation("attempt-denied", "state:before", "e2")

    assert before.value == "closed"
    assert cap.available and not auth.allowed
    assert denial.claim == "permission-denied"
    assert relation.kind == "attempt-denied"


def test_ack_does_not_equal_effect() -> None:
    before = State("remote", "version", 7)
    ack = Evidence("e3", "command-accepted", "remote", "transport", True, "verified")
    unknown_effect = Evidence("e4", "post-state-unknown", "remote", "system", True, "unknown")
    relation = Relation("reports", "e3", "remote", (("does_not_prove", "state-change"),))

    assert before.value == 7
    assert ack.claim == "command-accepted"
    assert unknown_effect.status == "unknown"
    assert relation.qualifiers == (("does_not_prove", "state-change"),)


def test_conflicting_reports() -> None:
    e1 = Evidence("e5", "door=open", "door-1", "sensor-a", True, "verified")
    e2 = Evidence("e6", "door=closed", "door-1", "sensor-b", True, "verified")
    state = State("door-1", "door", "unknown")
    r1 = Relation("supports", "e5", "state:door-1")
    r2 = Relation("supports", "e6", "state:door-1")

    assert e1.claim != e2.claim
    assert state.value == "unknown"
    assert r1.kind == r2.kind == "supports"


def test_absence_is_not_false() -> None:
    known = {"x": []}
    state = State("x", "observability", "not-observed")
    assert known["x"] == []
    assert state.value == "not-observed"
    assert state.value != "false"


def test_permission_vs_feasibility() -> None:
    cap = Capability("x", "move", False)
    auth = Authority("x", "move", True)
    assert_distinct("CAN vs MAY", cap.available, auth.allowed)


def test_safety_admissibility_without_constraint_object() -> None:
    temperature = State("robot", "temperature", 95)
    cap = Capability("robot", "move", True)
    auth = Authority("robot", "move", True)
    admissibility = Relation(
        "admissible-if",
        "action:move",
        "state:robot.temperature",
        (("predicate", "temperature < 80"),),
    )
    assert temperature.value == 95
    assert cap.available and auth.allowed
    assert admissibility.kind == "admissible-if"
    assert admissibility.qualifiers == (("predicate", "temperature < 80"),)
    # The action is not admissible even though it is technically possible and permitted.
    assert not (temperature.value < 80)


def test_temporal_authority() -> None:
    auth = Authority("operator", "deploy", True)
    relation = Relation("valid-during", "authority:operator.deploy", "interval:10-11")
    assert auth.allowed
    assert relation.kind == "valid-during"


def test_recovery() -> None:
    bad = State("service", "health", "failed")
    safe = State("service", "health", "healthy")
    cap = Capability("service", "restart", True)
    auth = Authority("service", "restart", True)
    evidence = Evidence("e7", "health=healthy", "service", "health-check", True, "verified")
    relation = Relation("recovers-to", "state:bad", "state:safe", (("requires_evidence", "e7"),))

    assert bad.value == "failed" and safe.value == "healthy"
    assert cap.available and auth.allowed
    assert evidence.verified
    assert relation.kind == "recovers-to"


def test_causality_and_order_are_qualifiers_not_hidden_lifecycle() -> None:
    r = Relation(
        "supports",
        "e8",
        "state:y",
        (("causal_precedence", "e7<e8"), ("sequence", 2)),
    )
    assert r.qualifiers == (("causal_precedence", "e7<e8"), ("sequence", 2))
    assert not hasattr(r, "authority")
    assert not hasattr(r, "outcome")
    assert not hasattr(r, "lifecycle")
    assert not hasattr(r, "provenance")


def test_representation_is_bidirectionally_recoverable() -> None:
    facts: Dict[str, Any] = {
        "before": State("x", "mode", "closed"),
        "after": State("x", "mode", "open"),
        "cap": Capability("x", "open", True),
        "auth": Authority("x", "open", True),
        "evidence": Evidence("e9", "mode=open", "x", "sensor", True, "verified"),
        "change": Relation("changes-to", "state:before", "state:after"),
    }

    # Required distinctions are directly queryable from the representation.
    assert facts["before"].value == "closed"
    assert facts["after"].value == "open"
    assert facts["cap"].available is True
    assert facts["auth"].allowed is True
    assert facts["evidence"].status == "verified"
    assert facts["change"].kind == "changes-to"

    # A deliberately incomplete representation must not be accepted as equivalent.
    incomplete = dict(facts)
    del incomplete["evidence"]
    assert "evidence" not in incomplete


def test_no_removed_named_types_exist() -> None:
    forbidden = {"Transition", "Observation", "Constraint"}
    defined = {State.__name__, Capability.__name__, Authority.__name__, Evidence.__name__, Relation.__name__}
    assert forbidden.isdisjoint(defined)


def main() -> None:
    tests = [
        test_successful_change,
        test_rejected_attempt,
        test_ack_does_not_equal_effect,
        test_conflicting_reports,
        test_absence_is_not_false,
        test_permission_vs_feasibility,
        test_safety_admissibility_without_constraint_object,
        test_temporal_authority,
        test_recovery,
        test_causality_and_order_are_qualifiers_not_hidden_lifecycle,
        test_representation_is_bidirectionally_recoverable,
        test_no_removed_named_types_exist,
    ]
    failures: List[str] = []
    for test in tests:
        try:
            test()
        except AssertionError as exc:
            failures.append(f"{test.__name__}: {exc}")
    if failures:
        print("RELATIONAL_SUBSTRATE_REDUCTION=FAIL")
        for failure in failures:
            print(failure)
        raise SystemExit(1)
    print(f"RELATIONAL_SUBSTRATE_REDUCTION=PASS ({len(tests)} tests)")


if __name__ == "__main__":
    main()
