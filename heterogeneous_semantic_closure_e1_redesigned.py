"""Genesis E1 redesigned bounded probe.

Case acceptance conditions are defined independently of the candidate schema.
Removal is an actual data counterfactual. This remains a bounded model and does
not prove ontology completeness or global minimality.
"""
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class TransitionCase:
    state_before: str
    state_after: str
    capability: str
    authority: str
    observation: str
    evidence: str
    constraint: str

CASES = {
    "math": TransitionCase("problem", "solved", "compute", "authorized", "result-observed", "proof-supported", "domain-valid"),
    "robotics": TransitionCase("pose0", "pose1", "move", "authorized", "pose-observed", "sensor-supported", "collision-free"),
    "governance": TransitionCase("proposal", "approved", "propose", "authorized", "decision-observed", "record-supported", "policy-valid"),
    "recovery": TransitionCase("failed", "recovered", "recover", "authorized", "recovery-observed", "diagnostic-supported", "safe-state"),
}

FIELDS = ("state_before", "state_after", "capability", "authority", "observation", "evidence", "constraint")

# Independently stated workflow invariants.
def accepted(case, x):
    if case == "math":
        return x.state_before == "problem" and x.state_after == "solved" and x.evidence == "proof-supported"
    if case == "robotics":
        return x.capability == "move" and x.observation == "pose-observed" and x.constraint == "collision-free"
    if case == "governance":
        return x.authority == "authorized" and x.observation == "decision-observed" and x.constraint == "policy-valid"
    if case == "recovery":
        return x.state_before == "failed" and x.state_after == "recovered" and x.evidence == "diagnostic-supported"
    return False


def closure_check():
    assert len(CASES) == 4
    assert all(accepted(case, value) for case, value in CASES.items())


def removal_counterfactuals():
    witnesses = {
        ("math", "state_before"), ("math", "state_after"), ("math", "evidence"),
        ("robotics", "capability"), ("robotics", "observation"), ("robotics", "constraint"),
        ("governance", "authority"), ("governance", "observation"), ("governance", "constraint"),
        ("recovery", "state_before"), ("recovery", "state_after"), ("recovery", "evidence"),
    }
    for case, field in witnesses:
        original = CASES[case]
        mutated = replace(original, **{field: None})
        assert accepted(case, original)
        assert not accepted(case, mutated), (case, field)
    assert len(witnesses) == 12


def schema_nonproliferation_check():
    # The common record uses only candidate-basis fields; no domain engine name
    # becomes a schema key.
    forbidden = {"Robot", "Sensor", "ResearchEngine", "Coordinator", "GovernanceEngine", "EvolutionEngine"}
    assert set(FIELDS).isdisjoint(forbidden)


def main():
    closure_check()
    removal_counterfactuals()
    schema_nonproliferation_check()
    print("E1 redesigned heterogeneous semantic closure: 1 closure + 12 removal witnesses + 1 schema check PASS")
    print("Status: BOUNDED MODEL ONLY")

if __name__ == "__main__":
    main()
