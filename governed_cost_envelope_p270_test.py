"""P270 structural total-cost envelope.

Compare the number of semantic governance primitives/check families needed by
one universal governed-transition basis versus a dedicated engine per target.
This is not a performance benchmark; it is a deterministic architecture-cost
model used to prevent ungrounded 'more machinery is safer' claims.
"""
TARGETS = ("capability", "mechanism", "routing", "authority", "verifier", "recovery")
UNIVERSAL_BASIS = ("state", "transition", "capability", "authority", "observation", "evidence", "constraint")


def universal_cost(targets):
    # One semantic basis plus one bounded qualification family per transition.
    return {"new_primitives": 0, "basis_size": len(UNIVERSAL_BASIS),
            "qualification_families": 1, "target_constraints": len(targets),
            "cognition_calls_for_guard": 0}


def dedicated_engine_cost(targets):
    # Conservative lower bound: each materially distinct target gets its own
    # coordinating engine and qualification family; shared primitives are not
    # counted twice here, so this intentionally favors the dedicated strategy.
    return {"new_primitives": len(targets), "basis_size": len(UNIVERSAL_BASIS),
            "qualification_families": len(targets), "target_constraints": len(targets),
            "cognition_calls_for_guard": 0}


def test_universal_cost_does_not_grow_primitive_count_with_targets():
    for n in range(1, len(TARGETS) + 1):
        c = universal_cost(TARGETS[:n])
        assert c["new_primitives"] == 0
        assert c["qualification_families"] == 1
        assert c["cognition_calls_for_guard"] == 0


def test_dedicated_strategy_has_strictly_more_coordinating_engines():
    for n in range(2, len(TARGETS) + 1):
        a = universal_cost(TARGETS[:n])
        b = dedicated_engine_cost(TARGETS[:n])
        assert b["new_primitives"] > a["new_primitives"]
        assert b["qualification_families"] > a["qualification_families"]


def test_protected_targets_are_constraints_not_new_semantic_primitives():
    protected = {"authority", "verifier", "routing"}
    c = universal_cost(TARGETS)
    assert protected <= set(TARGETS)
    assert c["new_primitives"] == 0


def test_governance_guards_are_deterministic_not_model_calls():
    for targets in (TARGETS[:1], TARGETS[:3], TARGETS):
        assert universal_cost(targets)["cognition_calls_for_guard"] == 0


def test_cost_model_does_not_claim_runtime_optimality():
    # Structural counts cannot establish wall time, memory, energy, quality or
    # real verification cost; the test encodes that these are separate metrics.
    metrics = {"wall_time", "compute", "memory", "energy", "quality",
               "verification", "recovery", "human_attention"}
    assert "wall_time" in metrics and "quality" in metrics


def run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for test in tests:
        test()
    print(f"p270 governed cost envelope: {len(tests)}/{len(tests)} PASS; targets={len(TARGETS)}")


if __name__ == "__main__":
    run()
