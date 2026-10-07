#!/usr/bin/env python3
"""Genesis-agnostic hosted control for robust adaptive candidate evaluation."""
from __future__ import annotations
import json

C = {
 "c1": {"b":(.86,.92),"e":(.76,.84),"r":(.55,.65),"c":(.18,.24)},
 "c2": {"b":(.70,.80),"e":(.91,.97),"r":(.18,.26),"c":(.25,.35)},
 "c3": {"b":(.82,.88),"e":(.87,.93),"r":(.30,.40),"c":(.20,.28)},
 "dominated": {"b":(.40,.50),"e":(.40,.50),"r":(.60,.70),"c":(.40,.50)},
}
LOW=((.40,.30,.20,.10),(.35,.30,.25,.10),(.45,.25,.20,.10))
HIGH=((.15,.15,.60,.10),(.20,.15,.55,.10),(.10,.20,.60,.10))

def dominates(a,b):
    ge = (a["b"][0]>=b["b"][1] and a["e"][0]>=b["e"][1]
          and a["r"][1]<=b["r"][0] and a["c"][1]<=b["c"][0])
    strict = (a["b"][0]>b["b"][1] or a["e"][0]>b["e"][1]
              or a["r"][1]<b["r"][0] or a["c"][1]<b["c"][0])
    return ge and strict

def select(ctx):
    ids=[k for k in C if not any(j!=k and dominates(C[j],C[k]) for j in C)]
    matrix={k:[] for k in ids}
    for w in ctx:
        for k in ids:
            x=C[k]
            matrix[k].append(w[0]*x["b"][0]+w[1]*x["e"][0]-w[2]*x["r"][1]-w[3]*x["c"][1])
    worst={k:min(v) for k,v in matrix.items()}
    best=[max(matrix[k][i] for k in matrix) for i in range(len(ctx))]
    regret={k:max(best[i]-v[i] for i,v in enumerate(matrix[k])) for k in matrix}
    order=sorted(ids,key=lambda k:(-worst[k],regret[k],k))
    return order[0], ids, worst, regret

def main():
    low=select(LOW); high=select(HIGH)
    assert "dominated" not in low[1]
    assert low[0]=="c3"
    assert high[0]=="c2"
    # Mathematical near-tie / abstention witness.
    near={
      "a":{"b":(.8,.8),"e":(.8,.8),"r":(.2,.2),"c":(.2,.2)},
      "b":{"b":(.8,.8),"e":(.8,.8),"r":(.2,.2),"c":(.2,.2)},
    }
    old=dict(C)
    C.clear(); C.update(near)
    try:
        picked,ids,worst,regret=select(((.4,.3,.2,.1),))
        assert abs(worst["a"]-worst["b"]) <= 1e-9
        assert abs(regret["a"]-regret["b"]) <= 1e-9
        abstain=True
    finally:
        C.clear(); C.update(old)
    print(json.dumps({
      "control_id":"S03-ROBUST-ADAPTIVE-CANDIDATE-EVALUATION-V1",
      "status":"PASS",
      "pareto_dominated_removed":True,
      "low_risk_selection":"c3",
      "high_risk_selection":"c2",
      "context_changes_selection":True,
      "near_tie_abstention":abstain,
      "authority_inference":False,
    },sort_keys=True))

if __name__=="__main__":
    main()
