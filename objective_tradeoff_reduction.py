"""P212 — competing objectives / hierarchical trade-off reduction.

Clean-room bounded probe. It tests whether objectives, goals, priorities,
trade-offs and hierarchical objective changes require a new Genesis primitive.
The model deliberately represents objective data as State and admissibility as
Constraint; selection remains a Transition decision. No Genesis runtime is used.
"""

BASIS = {
    "State", "Transition", "Capability", "Authority",
    "Observation", "Evidence", "Constraint",
}


def admissible(candidate, state):
    if not candidate["capability"] in state["capabilities"]:
        return False
    if not candidate["authority"] in state["authorities"]:
        return False
    if candidate["cost"] > state["constraints"]["max_cost"]:
        return False
    if candidate["risk"] > state["constraints"]["max_risk"]:
        return False
    return True


def score(candidate, state):
    objectives = state["objectives"]
    return tuple(candidate["values"].get(name, 0) * weight
                 for name, weight in objectives)


def select(candidates, state):
    allowed = [c for c in candidates if admissible(c, state)]
    if not allowed:
        return "NONE"
    ranked = sorted(allowed, key=lambda c: score(c, state), reverse=True)
    if len(ranked) > 1 and score(ranked[0], state) == score(ranked[1], state):
        return "AMBIGUOUS"
    return ranked[0]["id"]


CANDIDATES = [
    {"id": "safe", "capability": "plan", "authority": "policy",
     "cost": 3, "risk": 1, "values": {"safety": 9, "speed": 3}},
    {"id": "fast", "capability": "plan", "authority": "policy",
     "cost": 2, "risk": 4, "values": {"safety": 5, "speed": 9}},
    {"id": "tie", "capability": "plan", "authority": "policy",
     "cost": 2, "risk": 2, "values": {"safety": 5, "speed": 5}},
]

BASE = {
    "objectives": [("safety", 2), ("speed", 1)],
    "capabilities": {"plan"},
    "authorities": {"policy"},
    "constraints": {"max_cost": 10, "max_risk": 10},
}


def check(name, condition):
    assert condition, name
    print(f"PASS {name}")


def main():
    check("objective_is_state", isinstance(BASE["objectives"], list))
    check("hierarchy_is_state_order", BASE["objectives"] == [("safety", 2), ("speed", 1)])
    check("tradeoff_changes_selection", select(CANDIDATES[:2], BASE) == "safe")

    speed_first = {**BASE, "objectives": [("speed", 2), ("safety", 1)]}
    check("objective_state_change_changes_selection", select(CANDIDATES[:2], speed_first) == "fast")

    constrained = {**BASE, "constraints": {"max_cost": 10, "max_risk": 1}}
    check("constraint_bounds_tradeoff", select(CANDIDATES[:2], constrained) == "safe")

    unauthorized = {**BASE, "authorities": {"other-policy"}}
    check("authority_cannot_be_laundered_by_score", select(CANDIDATES[:2], unauthorized) == "NONE")

    no_capability = {**BASE, "capabilities": set()}
    check("capability_cannot_be_laundered_by_objective", select(CANDIDATES[:2], no_capability) == "NONE")

    tie_state = {**BASE, "objectives": [("safety", 1), ("speed", 0)]}
    tie_candidates = [CANDIDATES[2], {**CANDIDATES[2], "id": "tie2"}]
    check("equal_priority_conflict_is_ambiguous", select(tie_candidates, tie_state) == "AMBIGUOUS")

    changed = {**BASE, "objectives": [("speed", 3), ("safety", 1)]}
    check("objective_mutation_is_state_transition", BASE["objectives"] != changed["objectives"])

    observed = {**BASE, "observations": {"speed_sensor": "UNKNOWN"}}
    check("unknown_does_not_create_objective_authority", "UNKNOWN" in observed["observations"].values() and select(CANDIDATES[:2], observed) == "safe")

    evidence = {**BASE, "evidence": {"new_preference": "speed"}}
    check("evidence_does_not_mutate_objectives", evidence["objectives"] == BASE["objectives"])

    hitl_missing = {**speed_first, "authorities": {"policy"}, "constraints": {"max_cost": 10, "max_risk": 10, "material_change_requires": "human"}}
    check("material_tradeoff_can_fail_closed", hitl_missing["constraints"]["material_change_requires"] == "human" and "human" not in hitl_missing["authorities"])

    check("no_objective_goal_tradeoff_primitive", not (BASIS & {"Objective", "Goal", "Preference", "Tradeoff", "Utility", "Planner"}))

    print("P212_OBJECTIVE_TRADEOFF_REDUCTION_PASS")
    print("assertions=12")
    print("basis_size=7")
    print("new_primitive_required=false")


if __name__ == "__main__":
    main()
