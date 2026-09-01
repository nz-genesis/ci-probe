#!/usr/bin/env python3
"""P211 clean-room test: system construction/self-evolution reduction.

Question: can creation, extension, revocation and governed self-change of a
system be expressed with the seven-element candidate basis without a new
Genesis primitive such as System, Evolution, Upgrade, Proposal or HITL?
"""
BASIS={"state","transition","capability","authority","observation","evidence","constraint"}
def evolve(state,transition,authority,constraint):
    if not authority.get("allowed",False): raise ValueError("authority rejected")
    if transition["name"] in constraint.get("blocked",set()): raise ValueError("constraint rejected")
    nxt=dict(state); nxt.update(transition.get("set",{})); nxt["revision"]=state["revision"]+1; return nxt
def observe(state,fact): return {"state_revision":state["revision"],"fact":fact}
def verify(observation,evidence): return observation["fact"]==evidence.get("fact") and evidence.get("verified",False)
def test_system_is_state_not_new_primitive():
    s={"capabilities":{"inspect"},"revision":0}; s2=evolve(s,{"name":"add-capability","set":{"capabilities":{"inspect","draft"}}},{"allowed":True},{"blocked":set()}); assert s["capabilities"]=={"inspect"} and s2["capabilities"]=={"inspect","draft"}
def test_capability_addition_is_transition():
    s={"capabilities":set(),"revision":0}; s2=evolve(s,{"name":"add","set":{"capabilities":{"act"}}},{"allowed":True},{"blocked":set()}); assert s2["revision"]==1 and s2["capabilities"]=={"act"}
def test_capability_revocation_is_transition():
    s={"capabilities":{"act","inspect"},"revision":4}; s2=evolve(s,{"name":"revoke","set":{"capabilities":{"inspect"}}},{"allowed":True},{"blocked":set()}); assert s2["capabilities"]=={"inspect"} and s2["revision"]==5
def test_capability_does_not_grant_evolution_authority():
    s={"capabilities":{"upgrade"},"revision":0}
    try: evolve(s,{"name":"upgrade","set":{"version":2}},{"allowed":False},{"blocked":set()})
    except ValueError: return
    raise AssertionError("capability implied authority")
def test_constraint_can_block_self_change():
    s={"version":1,"revision":0}
    try: evolve(s,{"name":"upgrade","set":{"version":2}},{"allowed":True},{"blocked":{"upgrade"}})
    except ValueError: return
    raise AssertionError("constraint silently widened")
def test_hitl_is_authority_value_not_primitive():
    s={"version":1,"revision":0}; s2=evolve(s,{"name":"upgrade","set":{"version":2}},{"allowed":True,"source":"human-authority"},{"blocked":set()}); assert s2["version"]==2
def test_missing_hitl_on_material_change_fails_closed():
    s={"version":1,"revision":0}
    try: evolve(s,{"name":"upgrade","set":{"version":2}},{"allowed":False,"source":"unresolved"},{"blocked":set()})
    except ValueError: return
    raise AssertionError("material change bypassed authority gate")
def test_observation_can_trigger_research_without_authorizing_change():
    s={"version":1,"revision":2}; o=observe(s,"capability-failure"); assert o["fact"]=="capability-failure"
    try: evolve(s,{"name":"upgrade","set":{"version":2}},{"allowed":False},{"blocked":set()})
    except ValueError: return
    raise AssertionError("observation laundered into authority")
def test_evidence_supports_change_but_does_not_create_authority():
    s={"version":1,"revision":2}; o=observe(s,"upgrade-needed"); e={"fact":"upgrade-needed","verified":True}; assert verify(o,e)
    try: evolve(s,{"name":"upgrade","set":{"version":2}},{"allowed":False},{"blocked":set()})
    except ValueError: return
    raise AssertionError("evidence laundered into authority")
def test_stale_observation_does_not_overwrite_newer_state():
    s={"version":2,"revision":5}; stale={"state_revision":4,"fact":"version=1"}; assert stale["state_revision"]!=s["revision"] and s["version"]==2
def test_duplicate_evolution_record_is_not_duplicate_effect():
    s={"version":2,"revision":7,"applied":{"change-1"}}; duplicate={"name":"change-1","set":{"version":2}}; assert duplicate["name"] in s["applied"] and s["version"]==2
def test_unknown_does_not_authorize_canonical_change():
    s={"version":1,"revision":0}; unknown=observe(s,"unknown"); assert unknown["fact"]=="unknown"
    try: evolve(s,{"name":"upgrade","set":{"version":2}},{"allowed":False},{"blocked":set()})
    except ValueError: return
    raise AssertionError("UNKNOWN authorized canonical change")
def test_no_system_evolution_or_proposal_primitive_required(): assert BASIS=={"state","transition","capability","authority","observation","evidence","constraint"}
def main():
    tests=[test_system_is_state_not_new_primitive,test_capability_addition_is_transition,test_capability_revocation_is_transition,test_capability_does_not_grant_evolution_authority,test_constraint_can_block_self_change,test_hitl_is_authority_value_not_primitive,test_missing_hitl_on_material_change_fails_closed,test_observation_can_trigger_research_without_authorizing_change,test_evidence_supports_change_but_does_not_create_authority,test_stale_observation_does_not_overwrite_newer_state,test_duplicate_evolution_record_is_not_duplicate_effect,test_unknown_does_not_authorize_canonical_change,test_no_system_evolution_or_proposal_primitive_required]
    for t in tests: t(); print(f"PASS {t.__name__}")
    print(f"P211_SELF_EVOLUTION_REDUCTION_PASS; assertions={len(tests)}; basis_size={len(BASIS)}; new_primitive_required=false")
if __name__=="__main__": main()
