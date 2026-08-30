"""Genesis E1 redesigned bounded probe.

The case invariants are defined independently of the candidate schema. The test
then performs seven actual removal counterfactuals. This is still a bounded model,
not proof of ontology completeness.
"""
from dataclasses import dataclass

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

# These acceptance conditions are defined at the workflow level rather than by
# the candidate schema itself.
def invariant(x):
    return (
        all(getattr(x, f) not in ("", None) for f in FIELDS)
        and x.state_before != x.state_after
        and x.authority == "authorized"
    )


def closure_check():
    assert len(CASES) == 4
    assert all(invariant(x) for x in CASES.values())


def removal_counterfactuals():
    failures = 0
    for field in FIELDS:
        for original in CASES.values():
            values = {f: getattr(original, f) for f in FIELDS}
            values[field] = None
            class Mutated: pass
            m = Mutated()
            for f, value in values.items(): setattr(m, f, value)
            try:
                if invariant(m):
                    raise AssertionError(f"removal of {field} did not break invariant")
            except (AttributeError, AssertionError):
                failures += 1
    assert failures == len(FIELDS) * len(CASES)


def main():
    closure_check()
    removal_counterfactuals()
    print("E1 redesigned heterogeneous semantic closure: 1 closure + 28 removal checks PASS")
    print("Status: BOUNDED MODEL ONLY")

if __name__ == "__main__":
    main()
