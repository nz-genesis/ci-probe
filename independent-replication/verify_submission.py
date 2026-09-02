#!/usr/bin/env python3
"""Ontology-agnostic structural verifier for IR-V1 submissions."""
import argparse, hashlib, json, sys
from pathlib import Path

REQ=["basis","case_mappings","deletion_analysis","counterexamples","uncertainty","provenance","candidate_visibility"]
TOPICS=["authority","evidence","identity","provenance","execution","relation"]

def fail(msg):
    print("FAIL: "+msg); return 1

def main():
    p=argparse.ArgumentParser(); p.add_argument("submission"); p.add_argument("--challenge",default=str(Path(__file__).with_name("challenge-v1.json"))); a=p.parse_args()
    try: s=json.loads(Path(a.submission).read_text(encoding="utf-8")); c=json.loads(Path(a.challenge).read_text(encoding="utf-8"))
    except Exception as e: return fail("invalid JSON: "+str(e))
    for k in REQ:
        if k not in s:return fail("missing field: "+k)
    if c.get("challenge_id")!="IR-V1":return fail("wrong challenge")
    b=s["basis"]
    if not isinstance(b,list) or not b:return fail("basis must be non-empty list")
    ids=[x.get("id") for x in b if isinstance(x,dict)]
    if len(ids)!=len(b) or len(set(ids))!=len(ids) or any(not x for x in ids):return fail("basis ids must be unique")
    cases={x["id"] for x in c["cases"]}; mapped=set()
    for m in s["case_mappings"]:
        if not all(k in m for k in ("case_id","basis_ids","justification")):return fail("invalid case mapping")
        if m["case_id"] not in cases:return fail("unknown case id")
        if not m["basis_ids"] or not set(m["basis_ids"]).issubset(ids):return fail("mapping references unknown basis")
        if not str(m["justification"]).strip():return fail("empty justification")
        mapped.add(m["case_id"])
    if mapped!=cases:return fail("not all cases mapped")
    dels=s["deletion_analysis"]
    dids={x.get("basis_id") for x in dels if isinstance(x,dict)}
    if dids!=set(ids):return fail("deletion analysis must cover every basis item")
    if any(not str(x.get("justification","")).strip() for x in dels):return fail("empty deletion justification")
    text=" ".join(map(str,s["counterexamples"])).lower()
    for t in TOPICS:
        if t not in text:return fail("counterexample coverage missing: "+t)
    if not str(s["uncertainty"]).strip() or not str(s["provenance"]).strip():return fail("uncertainty/provenance required")
    if not isinstance(s["candidate_visibility"],(str,bool)):return fail("candidate_visibility must be explicit")
    print("PASS schema")
    print("PASS challenge_sha256="+hashlib.sha256(Path(a.challenge).read_bytes()).hexdigest())
    print(f"PASS case_coverage={len(cases)}/{len(cases)}")
    print(f"PASS deletion_coverage={len(ids)}/{len(ids)}")
    print("PASS anti_laundering_topics")
    print("PASS uncertainty_provenance")
    print("PASS candidate_visibility")
    print("NOTE semantic adequacy and agreement with any target hypothesis are not judged")
    return 0

if __name__=="__main__":sys.exit(main())
