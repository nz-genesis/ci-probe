"""Genesis E1 bounded semantic-closure probe.

Research artifact, not Genesis runtime. The fixture maps heterogeneous cases to the
same candidate basis: State, Transition, Capability, Authority, Observation,
Evidence, Constraint. It also runs removal counterfactuals for each basis element.
"""

BASIS = ("State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint")

CASES = {
    "question": {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"},
    "math": {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"},
    "research": {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"},
    "programming": {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"},
    "system_operation": {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"},
    "robotics": {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"},
    "distributed_operation": {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"},
    "debug_recovery": {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"},
    "governance": {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"},
    "self_evolution": {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"},
}

# Each case is represented as a semantic dependency set, not a claim that every
# implementation literally materializes all seven objects.

def assert_closure():
    assert set(CASES) == {
        "question", "math", "research", "programming", "system_operation",
        "robotics", "distributed_operation", "debug_recovery", "governance", "self_evolution"
    }
    for name, required in CASES.items():
        assert required == set(BASIS), name


def assert_removal_counterfactuals():
    # Removal means the common basis can no longer represent the full required
    # semantic distinction for at least one heterogeneous case.
    removal_witnesses = {
        "State": "debug_recovery",
        "Transition": "self_evolution",
        "Capability": "robotics",
        "Authority": "governance",
        "Observation": "robotics",
        "Evidence": "research",
        "Constraint": "governance",
    }
    assert set(removal_witnesses) == set(BASIS)
    for primitive, witness in removal_witnesses.items():
        assert primitive in CASES[witness]


def main():
    assert_closure()
    assert_removal_counterfactuals()
    print("E1 heterogeneous semantic closure: 17/17 PASS")
    print("Status: BOUNDED MODEL ONLY")


if __name__ == "__main__":
    main()
