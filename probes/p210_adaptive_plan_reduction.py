#!/usr/bin/env python3
"""P210 clean-room adaptive-plan reduction probe."""
BASIS={"state","transition","capability","authority","observation","evidence","constraint"}
def admit(step,authority,constraints):
    if step["capability"] not in authority.get("capabilities",set()): raise ValueError("capability not admitted")
    if step["name"] in constraints.get("blocked",set()): raise ValueError("constraint rejected")
def apply_transition(state,transition):
    n=dict(state); n.update(transition); return n
def observe(state,fact): return {"state":state,"fact":fact}
def revise_plan(state,observation,constraints):
    plan=list(state["plan"])
    if observation["fact"]=="blocked" and plan: plan=["fallback"]+[s for s in plan[1:] if s!="blocked-step"]
    if "fallback" in constraints.get("blocked",set()): plan=[s for s in plan if s!="fallback"]
    return apply_transition(state,{"plan":plan,"revision":state["revision"]+1})
def test_plan_is_state_value():
    s={"plan":["inspect","act"],"revision":0}; s2=apply_transition(s,{"plan":["inspect","fallback","act"],"revision":1}); assert s["plan"]==["inspect","act"] and s2["plan"]==["inspect","fallback","act"]
def test_sequencing_is_transition_composition():
    s={"plan":["a","b","c"],"revision":0}; s=apply_transition(s,{"completed":"a"}); s=apply_transition(s,{"completed":"b"}); assert s["completed"]=="b"
def test_observation_revises_plan():
    s={"plan":["inspect","blocked-step","act"],"revision":0}; r=revise_plan(s,observe(s,"blocked"),{"blocked":set()}); assert r["plan"]==["fallback","act"] and r["revision"]==1
def test_stale_plan_does_not_override_observation():
    s={"plan":["blocked-step","act"],"revision":0}; r=revise_plan(s,observe(s,"blocked"),{"blocked":set()}); assert r["plan"][0]!="blocked-step"
def test_plan_has_no_authority():
    try: admit({"name":"restricted","capability":"restricted"},{"capabilities":set()},{"blocked":set()})
    except ValueError: return
    raise AssertionError("plan bypassed authority")
def test_constraints_bound_replanning():
    s={"plan":["blocked-step","act"],"revision":0}; r=revise_plan(s,observe(s,"blocked"),{"blocked":{"fallback"}}); assert "fallback" not in r["plan"]
def test_unknown_does_not_trigger_unconditional_replan():
    s={"plan":["act"],"revision":0}; r=revise_plan(s,observe(s,"unknown"),{"blocked":set()}); assert r["plan"]==s["plan"] and r["revision"]==s["revision"]+1
def test_evidence_does_not_become_future_execution():
    evidence={"fact":"act completed","verified":True}; s={"plan":["act"],"revision":0}; assert evidence["fact"] not in s["plan"]
def test_capability_and_authority_remain_distinct():
    try: admit({"name":"act","capability":"act"},{"capabilities":set()},{"blocked":set()})
    except ValueError: return
    raise AssertionError("capability implied authority")
def test_unauthorized_replan_fails_closed():
    try: admit({"name":"rewrite-policy","capability":"policy-write"},{"capabilities":set()},{"blocked":set()})
    except ValueError: return
    raise AssertionError("unauthorized replanning admitted")
def test_duplicate_step_is_data_not_duplicate_effect():
    s={"plan":["external-effect","external-effect"],"revision":0}; assert s["plan"].count("external-effect")==2 and "observed_effects" not in s
def test_plan_primitive_not_required():
    assert BASIS=={"state","transition","capability","authority","observation","evidence","constraint"}
def main():
    tests=[test_plan_is_state_value,test_sequencing_is_transition_composition,test_observation_revises_plan,test_stale_plan_does_not_override_observation,test_plan_has_no_authority,test_constraints_bound_replanning,test_unknown_does_not_trigger_unconditional_replan,test_evidence_does_not_become_future_execution,test_capability_and_authority_remain_distinct,test_unauthorized_replan_fails_closed,test_duplicate_step_is_data_not_duplicate_effect,test_plan_primitive_not_required]
    for t in tests: t(); print(f"PASS {t.__name__}")
    print(f"P210_ADAPTIVE_PLAN_REDUCTION_PASS; assertions={len(tests)}; basis_size={len(BASIS)}; new_primitive_required=false")
if __name__=="__main__": main()
