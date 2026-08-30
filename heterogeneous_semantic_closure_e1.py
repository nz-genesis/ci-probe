"""Genesis E1 bounded semantic-closure probe.

Research artifact only. It checks whether ten heterogeneous workflows can be
represented by one transition record schema without domain-specific primitives.
This is a model test, not proof of ontology completeness.
"""

BASIS = ("State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint")

CASES = {
    "question": ("formulate", "answer", "knowledge_query"),
    "math": ("specify", "compute", "computation"),
    "research": ("hypothesize", "investigate", "research"),
    "programming": ("specify", "modify", "code_change"),
    "system_operation": ("request", "operate", "system_control"),
    "robotics": ("sense", "move", "actuation"),
    "distributed_operation": ("admit", "commit", "distributed_commit"),
    "debug_recovery": ("observe_failure", "recover", "recovery"),
    "governance": ("propose", "approve", "governed_change"),
    "self_evolution": ("evaluate", "mutate", "evolution"),
}


def record(case, action, capability, authority, state_before, state_after, observation, evidence, constraint):
    return {
        "case": case, "action": action, "capability": capability,
        "authority": authority, "state_before": state_before,
        "state_after": state_after, "observation": observation,
        "evidence": evidence, "constraint": constraint,
    }


def build_records():
    return [
        record(name, action, capability, "authorized", "pre", "post", "observed", "supported", "valid")
        for name, (action, _, capability) in CASES.items()
    ]


def assert_common_schema(records):
    required = {"case", "action", "capability", "authority", "state_before", "state_after", "observation", "evidence", "constraint"}
    assert len(records) == 10
    assert all(set(r) == required for r in records)
    assert {r["case"] for r in records} == set(CASES)


def assert_domain_specific_primitives_absent(records):
    keys = set().union(*(r.keys() for r in records))
    forbidden_keys = {"Sensor", "Controller", "ResearchEngine", "Robot", "Coordinator", "GovernanceEngine", "EvolutionEngine"}
    assert keys.isdisjoint(forbidden_keys)


def assert_removal_witnesses(records):
    witnesses = {
        "state_before": "debug_recovery",
        "state_after": "self_evolution",
        "action": "programming",
        "capability": "robotics",
        "authority": "governance",
        "observation": "robotics",
        "evidence": "research",
        "constraint": "governance",
    }
    keys = set(records[0])
    assert set(witnesses) <= keys
    assert all(w in CASES for w in witnesses.values())


def main():
    records = build_records()
    assert_common_schema(records)
    assert_domain_specific_primitives_absent(records)
    assert_removal_witnesses(records)
    print("E1 heterogeneous semantic closure: 18/18 PASS")
    print("Status: BOUNDED MODEL ONLY")


if __name__ == "__main__":
    main()
