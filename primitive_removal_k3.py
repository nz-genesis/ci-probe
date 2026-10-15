"""Clean-room K3: heterogeneous primitive-removal stress test.

The fixture deliberately does not instantiate candidate-specific classes.
Each case stores semantic data plus an independently defined invariant
predicate. The goal is to test whether candidate dimensions can remain
compositional across materially different domains.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Case:
    domain: str
    candidate: str
    record: dict[str, str]
    invariant: str


CASES = (
    Case("research", "evidence", {"claim": "source supports result", "support": "independent"}, "support-is-explicit"),
    Case("software", "state", {"version": "v2", "status": "running"}, "current-version-is-explicit"),
    Case("governance", "authority", {"actor": "reviewer", "decision": "allow", "scope": "release"}, "authority-scope-is-explicit"),
    Case("robotics", "capability", {"actor": "arm", "operation": "move", "bound": "workspace"}, "capability-bound-is-explicit"),
    Case("distributed", "transition", {"before": "leader-A", "after": "leader-B", "cause": "election"}, "change-cause-is-explicit"),
    Case("recovery", "observation", {"source": "external", "signal": "effect-confirmed", "time": "late"}, "observation-provenance-is-explicit"),
    Case("self-evolution", "constraint", {"change": "policy-update", "invariant": "owner-approval-required"}, "invariant-is-explicit"),
)


def generic_representation(case: Case) -> tuple[tuple[str, str], ...]:
    return tuple(sorted(case.record.items())) + (("dimension", case.candidate), ("domain", case.domain))


def invariant(case: Case) -> bool:
    values = case.record
    checks = {
        "support-is-explicit": values.get("support") not in (None, ""),
        "current-version-is-explicit": values.get("version") not in (None, ""),
        "authority-scope-is-explicit": values.get("scope") not in (None, ""),
        "capability-bound-is-explicit": values.get("bound") not in (None, ""),
        "change-cause-is-explicit": values.get("cause") not in (None, ""),
        "observation-provenance-is-explicit": values.get("source") not in (None, ""),
        "invariant-is-explicit": values.get("invariant") not in (None, ""),
    }
    return checks[case.invariant]


def no_candidate_specific_type(case: Case) -> bool:
    # The candidate exists only as data; there is no candidate-specific class,
    # engine, manager, graph, or runtime object in this fixture.
    return type(case.record) is dict and type(generic_representation(case)) is tuple


def verify() -> None:
    assert len(CASES) == 7
    assert {case.candidate for case in CASES} == {
        "state", "transition", "capability", "authority", "observation", "evidence", "constraint"
    }
    assert len({case.domain for case in CASES}) == 7
    assert all(invariant(case) for case in CASES)
    assert all(no_candidate_specific_type(case) for case in CASES)


if __name__ == "__main__":
    verify()
    for case in CASES:
        print(f"{case.domain}/{case.candidate}: invariant=PASS generic-representation=PASS")
    print("primitive removal K3: PASS")
