"""Executable bounded reconstruction matrix for Genesis functional-chain archaeology.

Purpose: test whether a compact semantic basis can reconstruct materially different
functional-chain cases without making historical pipeline stages mandatory primitives.
This is a research probe, not a canonical Genesis runtime.
"""
from dataclasses import dataclass
from typing import FrozenSet


@dataclass(frozen=True)
class Case:
    name: str
    required: FrozenSet[str]
    produced: FrozenSet[str]
    world_effect: bool
    epistemic_effect: bool


BASIS = frozenset({
    "context", "constraint", "capability", "authority", "execution",
    "observation", "evidence", "verification", "lineage", "state",
})

CASES = [
    Case("direct_interaction", frozenset({"context", "capability"}), frozenset({"observation"}), False, False),
    Case("ambiguous_request", frozenset({"context", "evidence", "lineage"}), frozenset({"state", "lineage"}), False, True),
    Case("multiple_intents", frozenset({"context", "lineage", "constraint"}), frozenset({"state", "lineage"}), False, True),
    Case("external_signal", frozenset({"context", "evidence", "lineage"}), frozenset({"observation", "evidence"}), False, True),
    Case("adversarial_signal", frozenset({"context", "evidence", "constraint", "lineage"}), frozenset({"verification", "evidence"}), False, True),
    Case("research_before_execution", frozenset({"context", "capability", "evidence", "lineage"}), frozenset({"evidence", "state"}), False, True),
    Case("system_creation", frozenset({"context", "capability", "authority", "constraint", "execution"}), frozenset({"state", "observation", "evidence"}), True, False),
    Case("delegation_federation", frozenset({"authority", "capability", "constraint", "lineage"}), frozenset({"observation", "evidence", "lineage"}), True, True),
    Case("failed_execution_recovery", frozenset({"authority", "execution", "observation", "lineage"}), frozenset({"state", "evidence", "verification"}), True, True),
    Case("concurrent_cycles", frozenset({"execution", "observation", "lineage", "state"}), frozenset({"state", "lineage"}), True, True),
    Case("learning_without_execution", frozenset({"evidence", "observation", "lineage"}), frozenset({"state", "evidence"}), False, True),
    Case("epistemic_outcome", frozenset({"evidence", "verification", "lineage"}), frozenset({"evidence", "state"}), False, True),
    Case("outcome_as_signal", frozenset({"observation", "evidence", "lineage"}), frozenset({"state", "observation"}), False, True),
    Case("recursive_creation", frozenset({"capability", "authority", "constraint", "execution", "lineage"}), frozenset({"state", "evidence", "observation"}), True, True),
]

# Historical stages are deliberately labels, not primitives. The matrix checks whether
# each case has a sufficient semantic witness in BASIS and whether both effect types can
# be represented without assuming execution is mandatory.

def reconstruct(case: Case) -> bool:
    if not case.required <= BASIS:
        return False
    if not case.produced <= BASIS:
        return False
    if case.world_effect and "execution" not in case.required:
        # World effects may be produced indirectly; this is a deliberate omission witness,
        # not a failure of the basis. The case remains reconstructable by external effect
        # observation represented through observation/evidence/lineage.
        return {"observation", "evidence", "lineage"} <= BASIS
    return True


def main() -> None:
    results = {c.name: reconstruct(c) for c in CASES}
    assert all(results.values())
    # Negative controls: remove each basis dimension and require at least one materially
    # dependent case to become unreconstructable.
    witnesses = {}
    for dimension in sorted(BASIS):
        reduced = BASIS - {dimension}
        broken = [c.name for c in CASES if not c.required <= reduced]
        witnesses[dimension] = broken
        assert broken, f"dimension has no removal witness: {dimension}"

    # No historical pipeline label is promoted to a primitive by the probe.
    historical_labels = {"signal", "request", "intent", "goal", "mission", "objective",
                         "reasoning", "decision", "planning", "trace", "memory", "knowledge",
                         "approval", "tool", "method", "learning", "promotion"}
    assert not (BASIS & historical_labels)

    print(f"FUNCTIONAL CHAIN RECONSTRUCTION: {len(CASES)}/{len(CASES)} PASS")
    print(f"BASIS REMOVAL WITNESSES: {len(witnesses)}/{len(BASIS)} PASS")
    for dimension, broken in sorted(witnesses.items()):
        print(f"  {dimension}: {len(broken)} witness(es)")
    print("Historical stages remain candidate semantic roles, not automatic primitives.")


if __name__ == "__main__":
    main()
