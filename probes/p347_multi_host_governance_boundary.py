#!/usr/bin/env python3
"""P347 real multi-host protected-governance boundary probe."""
from __future__ import annotations
import base64, json, os, signal, socket, subprocess, sys, time
import urllib.error, urllib.request
from pathlib import Path

API = "https://api.github.com"
REPO = os.environ["GITHUB_REPOSITORY"]
BRANCH = os.environ["P347_BRANCH"]
TOKEN = os.environ.get("GITHUB_TOKEN") or os.environ["GH_TOKEN"]
RUN_ID = os.environ["GITHUB_RUN_ID"]
BASE = f"{API}/repos/{REPO}"
GOV_PATH = "probes/p347_state/governance.txt"
READY_PATH = f"probes/p347_state/worker-ready-{RUN_ID}.json"
PREPARE_PATH = f"probes/p347_state/prepare-{RUN_ID}.json"
EFFECT_PATH = "probes/p347_state/effect-seed.txt"
OUT = Path(os.environ.get("P347_OUT", "p347-result.json"))

def api(method: str, path: str, payload: dict | None = None):
    data = json.dumps(payload).encode() if payload is not None else None
    headers = {"Accept":"application/vnd.github+json","Authorization":f"Bearer {TOKEN}",
               "X-GitHub-Api-Version":"2026-03-10","User-Agent":"genesis-p347-probe"}
    if payload is not None:
        headers["Content-Type"]="application/json"
    req=urllib.request.Request(BASE+path,data=data,headers=headers,method=method)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with opener.open(req, timeout=20) as r:
            raw=r.read().decode()
            return r.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw=e.read().decode(errors="replace")
        try: body=json.loads(raw)
        except json.JSONDecodeError: body={"raw":raw}
        return e.code,body

def put_text(path,content,sha=None):
    payload={"message":f"P347: update {path}","content":base64.b64encode(content.encode()).decode(),"branch":BRANCH}
    if sha: payload["sha"]=sha
    return api("PUT",f"/contents/{path}",payload)

def get_text(path):
    status,body=api("GET",f"/contents/{path}?ref={BRANCH}")
    if status!=200: raise RuntimeError(f"GET {path}: HTTP {status}: {body}")
    return base64.b64decode(body["content"]).decode(),body["sha"]

def write_result(result):
    OUT.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n",encoding="utf-8")

def identity():
    return {"hostname":socket.gethostname(),"runner_name":os.environ.get("RUNNER_NAME"),
            "runner_os":os.environ.get("RUNNER_OS"),"runner_arch":os.environ.get("RUNNER_ARCH"),
            "job":os.environ.get("GITHUB_JOB"),"run_id":RUN_ID}

def block_api():
    lines=subprocess.check_output(["getent","ahosts","api.github.com"],text=True).splitlines()
    ipv4=sorted({x.split()[0] for x in lines if x.split() and "." in x.split()[0]})
    ipv6=sorted({x.split()[0] for x in lines if x.split() and ":" in x.split()[0]})
    for addr in ipv4:
        subprocess.run(["sudo","iptables","-A","OUTPUT","-p","tcp","-d",addr,"--dport","443","-j","REJECT"],check=True)
    for addr in ipv6:
        subprocess.run(["sudo","ip6tables","-A","OUTPUT","-p","tcp","-d",addr,"--dport","443","-j","REJECT"],check=True)
    return {"ipv4":ipv4,"ipv6":ipv6,"proxy_disabled":True}

def unblock_api(receipt):
    for addr in receipt["ipv4"]:
        subprocess.run(["sudo","iptables","-D","OUTPUT","-p","tcp","-d",addr,"--dport","443","-j","REJECT"],check=False)
    for addr in receipt["ipv6"]:
        subprocess.run(["sudo","ip6tables","-D","OUTPUT","-p","tcp","-d",addr,"--dport","443","-j","REJECT"],check=False)

def worker():
    me=identity()
    generation1,gate_sha=get_text(EFFECT_PATH)
    governance1,governance_sha=get_text(GOV_PATH)
    ready={"run_id":RUN_ID,"worker":me,"observed_generation":generation1,
           "observed_governance":governance1,"effect_blob_sha":gate_sha,
           "governance_blob_sha":governance_sha}
    status,_=put_text(READY_PATH,json.dumps(ready,sort_keys=True))
    if status not in (200,201): raise RuntimeError(f"ready write failed: HTTP {status}")
    prepare=json.dumps({"run_id":RUN_ID,"generation":1,"kind":"PREPARE","worker":me},sort_keys=True)
    ps,pb=put_text(PREPARE_PATH,prepare)
    if ps not in (200,201): raise RuntimeError(f"prepare effect failed: HTTP {ps}")
    child=os.fork()
    if child==0:
        Path(f"p347-child-crash-{RUN_ID}.marker").write_text("prepared-before-crash\n")
        os.kill(os.getpid(),signal.SIGKILL)
    _,child_status=os.waitpid(child,0)
    crashed=os.WIFSIGNALED(child_status) and os.WTERMSIG(child_status)==signal.SIGKILL
    addrs=block_api()
    try: time.sleep(15)
    finally: unblock_api(addrs)
    stale=json.dumps({"run_id":RUN_ID,"generation":1,"kind":"COMMIT","worker":me},sort_keys=True)
    ss,sb=put_text(EFFECT_PATH,stale,sha=gate_sha)
    result={"role":"worker_a","identity":me,"initial_effect_sha":gate_sha,
            "initial_governance_sha":governance_sha,"prepare_status":ps,
            "prepare_commit_sha":pb.get("commit",{}).get("sha"),
            "real_child_sigkill_observed":crashed,"partition_addresses":addrs,
            "stale_effect_status":ss,"stale_effect_rejected_409":ss==409,
            "stale_effect_response":sb}
    write_result(result)
    return 0 if crashed and ss==409 else 1

def authority():
    me=identity(); deadline=time.time()+90; ready=None
    while time.time()<deadline:
        status,body=api("GET",f"/contents/{READY_PATH}?ref={BRANCH}")
        if status==200:
            ready=json.loads(base64.b64decode(body["content"]).decode()); break
        time.sleep(2)
    if ready is None: raise RuntimeError("worker-ready marker did not appear")
    current,sha=get_text(EFFECT_PATH)
    if current.strip()!="GENERATION=1": raise RuntimeError(f"unexpected initial gate: {current!r}")
    status,body=put_text(EFFECT_PATH,"GENERATION=2\n",sha=sha)
    if status!=200: raise RuntimeError(f"authority mutation failed: HTTP {status}: {body}")
    write_result({"role":"authority","identity":me,"worker_identity":ready["worker"],
                  "observed_worker_generation":ready["observed_generation"],
                  "observed_worker_effect_sha":ready["effect_blob_sha"],
                  "authority_mutation_status":status,
                  "authority_mutation_commit_sha":body.get("commit",{}).get("sha"),
                  "new_effect_sha":body.get("content",{}).get("sha"),
                  "generation_after_mutation":2})
    return 0

def observer():
    me=identity(); final,sha=get_text(EFFECT_PATH)
    status,body=api("GET",f"/contents/{READY_PATH}?ref={BRANCH}")
    if status!=200: raise RuntimeError(f"ready unavailable: HTTP {status}")
    ready=json.loads(base64.b64decode(body["content"]).decode())
    result={"role":"observer","identity":me,"final_effect":final,"final_effect_sha":sha,
            "worker_identity":ready["worker"],
            "distinct_runner_hosts":me["hostname"]!=ready["worker"]["hostname"],
            "authoritative_final_generation_2":final.strip()=="GENERATION=2"}
    write_result(result)
    return 0 if result["distinct_runner_hosts"] and result["authoritative_final_generation_2"] else 1

if __name__=="__main__":
    raise SystemExit({"worker":worker,"authority":authority,"observer":observer}[sys.argv[1]]())
