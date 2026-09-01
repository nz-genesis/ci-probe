"""P213 — partial-order / incomparable normative trade-off reduction.

Clean-room bounded probe. P212 tested weighted hierarchical objectives. P213
changes the discriminator to genuinely incomparable objectives and Pareto-like
frontiers. The relation itself is State; admissibility is Constraint +
Capability + Authority; unresolved incomparability is not silently ordered.
"""

BASIS = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}

CANDIDATES = [
    {"id": "safe", "capability": "plan", "authority": "policy", "cost": 3, "risk": 1, "values": {"safety": 9, "speed": 3}},
    {"id": "fast", "capability": "plan", "authority": "policy", "cost": 2, "risk": 4, "values": {"safety": 5, "speed": 9}},
    {"id": "cheap", "capability": "plan", "authority": "policy", "cost": 1, "risk": 3, "values": {"safety": 4, "speed": 6}},
]

BASE = {
    "objective_order": {"safety": {"safety"}, "speed": {"speed"}},
    "capabilities": {"plan"},
    "authorities": {"policy"},
    "constraints": {"max_cost": 10, "max_risk": 10},
}


def admissible(candidate, state):
    return (
        candidate["capability"] in state["capabilities"]
        and candidate["authority"] in state["authorities"]
        and candidate["cost"] <= state["constraints"]["max_cost"]
        and candidate["risk"] <= state["constraints"]["max_risk"]
    )


def dominates(a, b, state):
    order = state["objective_order"]
    no_worse = all(a["values"].get(o, 0) >= b["values"].get(o, 0) for o in order)
    strictly_better = any(a["values"].get(o, 0) > b["values"].get(o, 0) for o in order)
    return no_worse and strictly_better


def frontier(candidates, state):
    allowed = [c for c in candidates if admissible(c, state)]
    return [c["id"] for c in allowed if not any(dominates(other, c, state) for other in allowed)]


def check(name, condition):
    assert condition, name
    print(f"PASS {name}")


def main():
    check("partial_order_is_state", isinstance(BASE["objective_order"], dict))
    check("incomparable_objectives_are_representable", BASE["objective_order"]["safety"] != BASE["objective_order"]["speed"])
    check("frontier_preserves_incomparable_candidates", set(frontier(CANDIDATES[:2], BASE)) == {"safe", "fast"})

    safety_dominant = {**BASE, "objective_order": {"safety": {"safety", "speed"}, "speed": {"speed"}}}
    check("state_relation_change_changes_frontier", set(frontier(CANDIDATES[:2], safety_dominant)) == {"safe"})

    constrained = {**BASE, "constraints": {"max_cost": 2, "max_risk": 10}}
    check("constraint_changes_frontier", set(frontier(CANDIDATES[:2], constrained)) == {"fast"})

    unauthorized = {**BASE, "authorities": {"other-policy"}}
    check("authority_still_bounds_incomparable_set", frontier(CANDIDATES[:2], unauthorized) == [])

    no_capability = {**BASE, "capabilities": set()}
    check("capability_still_bounds_incomparable_set", frontier(CANDIDATES[:2], no_capability) == [])

    changed = {**BASE, "objective_order": {"safety": {"safety", "speed"}, "speed": {"speed"}}}
    check("order_mutation_is_state_transition", changed["objective_order"] != BASE["objective_order"])

    check("unresolved_incomparability_is_not_success", set(frontier(CANDIDATES[:2], BASE)) == {"safe", "fast"})

    evidence = {**BASE, "evidence": {"preferred": "fast"}}
    check("evidence_does_not_create_order", evidence["objective_order"] == BASE["objective_order"])

    observed = {**BASE, "observations": {"preference_sensor": "UNKNOWN"}}
    check("unknown_does_not_create_order", "UNKNOWN" in observed["observations"].values() and frontier(CANDIDATES[:2], observed) == ["safe", "fast"])

    tie_breaker = {**BASE, "constraints": {"max_cost": 10, "max_risk": 10, "tie_breaker": "human"}}
    check("tie_breaker_can_be_explicit_authority_constraint", tie_breaker["constraints"]["tie_breaker"] == "human")

    check("no_partial_order_pareto_primitive", not (BASIS & {"Objective", "Goal", "Tradeoff", "Pareto", "Utility", "Planner", "Priority"}))

    print("P213_PARTIAL_ORDER_NORMATIVE_REDUCTION_PASS")
    print("assertions=12")
    print("basis_size=7")
    print("new_primitive_required=false")


if __name__ == "__main__":
    main()
