#!/usr/bin/env python3
"""P347 Mac actor. Never configures or activates the fault injector."""
import argparse, hashlib, json, os, platform, secrets, stat, subprocess, sys, tempfile, time, uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

META="__P347_META__"
SECRET_DIR=Path.home()/".local"/"share"/"p347-authority"
UA="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/154.0.0.0 Safari/537.36"

def utc(): return datetime.now(timezone.utc).isoformat()
def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def fingerprint(v): return hashlib.sha256(canon(v).encode()).hexdigest()
def transport(status,code): return "UNKNOWN" if status is None or code is None or code != 0 else "HTTP_RESPONSE_OBSERVED"
def text(v): return v.decode("utf-8","replace") if isinstance(v,bytes) else ("" if v is None else str(v))

def parse_curl(stdout,stderr,code):
    raw,err=text(stdout),text(stderr); at=raw.rfind(META); status=local=remote=port=elapsed=None; body=raw
    if at>=0:
        body=raw[:at].rstrip("\r\n"); fields=raw[at:].splitlines()[0][len(META):].strip().split("\t")
        if len(fields)==5:
            try:
                n=int(fields[0]) if fields[0].isdigit() else 0
                status=n if n>0 else None; local=fields[1] or None; remote=fields[2] or None
                port=int(fields[3]) if fields[3].isdigit() else None
                elapsed=float(fields[4]) if fields[4] else None
            except (ValueError,IndexError): status=None
    try: parsed=json.loads(body) if body else None
    except json.JSONDecodeError: parsed={"raw":body[:8192]} if body else None
    state=transport(status,code)
    return {"http_status":status,"local_ip":local,"remote_ip":remote,"remote_port":port,
            "curl_elapsed_seconds":elapsed,"curl_exit":code,"transport_state":state,
            "response_body":parsed,"transport_error":err[:2000] if state=="UNKNOWN" else None}

def request(url,method="GET",token=None,body=None,headers=None,timeout=20.0):
    if not url.startswith("https://"): raise ValueError("authority URL must use HTTPS")
    if timeout<=0: raise ValueError("timeout must be positive")
    cmd=["curl","--silent","--show-error","--ipv4","--http1.1","--connect-timeout","10",
         "--max-time",str(timeout),"--request",method.upper(),"--header","accept: application/json",
         "--header","user-agent: "+UA,"--write-out","\n"+META+"%{http_code}\t%{local_ip}\t%{remote_ip}\t%{remote_port}\t%{time_total}\n"]
    if body is not None: cmd += ["--header","content-type: application/json","--data-binary","@-"]
    for k,v in (headers or {}).items():
        if any(c in k+v for c in "\r\n"): raise ValueError("newline in HTTP header")
        cmd += ["--header",k+": "+v]
    start,start_ns=utc(),time.monotonic_ns()
    try:
        with tempfile.TemporaryDirectory(prefix="p347-curl-") as temp_dir:
            os.chmod(temp_dir,0o700)
            if token:
                auth_file=Path(temp_dir)/"authorization-header"
                auth_file.write_text("authorization: Bearer "+token+"\n",encoding="utf-8")
                auth_file.chmod(0o600)
                cmd += ["--header","@"+str(auth_file)]
            p=subprocess.run(cmd,input=None if body is None else canon(body),capture_output=True,text=True,timeout=timeout+5,check=False)
            result=parse_curl(p.stdout,p.stderr,p.returncode)
    except (subprocess.TimeoutExpired,OSError) as e:
        result={"http_status":None,"local_ip":None,"remote_ip":None,"remote_port":None,"curl_elapsed_seconds":None,
                "curl_exit":None,"transport_state":"UNKNOWN","response_body":None,"transport_error":type(e).__name__}
    parts=url.split("/",3)
    result.update({"method":method.upper(),"path":"/"+parts[3] if len(parts)==4 else "/",
      "request_started_utc":start,"request_started_monotonic_ns":start_ns,
      "request_finished_utc":utc(),"request_finished_monotonic_ns":time.monotonic_ns()})
    if body is not None: result["request_body"]=body
    if headers: result["nonsecret_request_headers"]=headers
    return result # Never return the Authorization value.

def source_sha():
    root=Path(__file__).resolve().parents[2]
    rev=subprocess.run(["git","rev-parse","HEAD"],cwd=root,capture_output=True,text=True,check=False)
    dirty=subprocess.run(["git","status","--porcelain","--untracked-files=normal"],cwd=root,capture_output=True,text=True,check=False)
    if rev.returncode or dirty.returncode or dirty.stdout.strip(): raise RuntimeError("actor requires a clean exact Git checkout")
    return rev.stdout.strip()

def save(root,run):
    p=root/"actor-evidence.json"; tmp=p.with_name(p.name+".tmp")
    with tmp.open("w",encoding="utf-8") as f: json.dump(run,f,ensure_ascii=False,indent=2,sort_keys=True); f.write("\n"); f.flush(); os.fsync(f.fileno())
    tmp.replace(p); p.chmod(0o600)

def event(root,value):
    p=root/"actor-events.jsonl"
    with p.open("a",encoding="utf-8") as f: f.write(json.dumps(value,sort_keys=True)+"\n"); f.flush(); os.fsync(f.fileno())
    p.chmod(0o600)

def secret(path):
    p=Path(path).expanduser()
    if not p.is_file(): raise RuntimeError("required credential file missing: "+str(p))
    if os.name=="posix" and stat.S_IMODE(p.stat().st_mode)&0o077: raise RuntimeError("credential permissions must be 0600 or stricter: "+str(p))
    value=p.read_text().strip()
    if not value: raise RuntimeError("credential file empty: "+str(p))
    return value

def load(root):
    r=json.loads((root/"actor-evidence.json").read_text())
    if r.get("schema")!="p347-mac-actor-v1": raise RuntimeError("unsupported evidence schema")
    return r

def body(r): return r["response_body"] if isinstance(r.get("response_body"),dict) else {}
def require(r,status,predicate,name):
    if r.get("http_status")!=status or r.get("transport_state")!="HTTP_RESPONSE_OBSERVED" or not predicate(body(r)):
        raise RuntimeError(name+" contract mismatch: "+json.dumps({"status":r.get("http_status"),"transport":r.get("transport_state"),"body":body(r)},sort_keys=True))

def call(root,run,name,method,path,token=None,payload=None,headers=None,timeout=20.0):
    r=request(run["authority_url"]+path,method,token,payload,headers,timeout)
    r.update({"name":name,"correlation_id":run["correlation_id"],"actor_host":run["actor_host"]})
    run.setdefault("calls",[]).append(r); event(root,{"event":"http_call_observed","name":name,"correlation_id":run["correlation_id"],
      "wall_time_utc":r["request_finished_utc"],"monotonic_ns":r["request_finished_monotonic_ns"],
      "http_status":r["http_status"],"transport_state":r["transport_state"],"local_ip":r["local_ip"],"remote_ip":r["remote_ip"],"remote_port":r["remote_port"]})
    save(root,run); return r

def prepare(a):
    root=Path(a.run_dir).expanduser().resolve(); root.mkdir(parents=True,mode=0o700,exist_ok=False); root.chmod(0o700)
    url=Path(a.authority_url_file).expanduser().read_text().strip().rstrip("/")
    if not url.startswith("https://") or ".workers.dev" not in url: raise RuntimeError("authority URL must be HTTPS workers.dev URL, not claim URL")
    admin,token=secret(a.admin_token_file),secret(a.effect_token_file); sha=source_sha()
    rid=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")+"-"+secrets.token_hex(4); eid="p347-mac-"+rid.lower()
    run={"schema":"p347-mac-actor-v1","run_id":rid,"correlation_id":str(uuid.uuid4()),"actor_host":platform.node(),
      "actor_platform":platform.platform(),"actor_source_version":sha,"source_version_expected":a.expected_source_version,
      "authority_url":url,"effect_id":eid,"stage":"PREPARING","started_at_utc":utc(),"calls":[],
      "fault_injector":{"owned_by_actor":False,"activated_by_actor":False,"receipt":None},
      "claims":{"lost_ack_exercised":False,"ambiguous_effect_recovery_verified":False,"physical_effect_admitted":False,"independent_witness_admitted":False}}
    save(root,run)
    s=call(root,run,"initial_state","GET","/v1/state")
    require(s,200,lambda b:b.get("authority")=="P347_EXTERNAL_AUTHORITY" and b.get("source_version")==a.expected_source_version and b.get("generation")==1 and b.get("effect_count")==0,"initial_state")
    m=call(root,run,"authority_mutation","POST","/v1/admin/mutate",admin,{})
    if m.get("http_status")==200 and body(m).get("generation")==2: run["mutation_disposition"]="RESPONSE_OBSERVED"
    else:
        # Never retry a generation mutation; resolve only by a fresh read.
        fresh=call(root,run,"mutation_fresh_state","GET","/v1/state")
        if fresh.get("http_status")!=200 or body(fresh).get("source_version")!=a.expected_source_version or body(fresh).get("generation")!=2:
            run["stage"]="STOPPED_MUTATION_AMBIGUOUS"; save(root,run); raise RuntimeError("mutation not confirmed by fresh state; do not retry")
        run["mutation_disposition"]="UNKNOWN_RESOLVED_BY_FRESH_STATE"
    stale={"generation":1,"payload":{"amount":0}}
    r=call(root,run,"stale_generation_reject","POST","/v1/effects",token,stale,{"Idempotency-Key":eid+"-stale",
      "X-Request-Fingerprint":fingerprint(stale),"X-Correlation-ID":run["correlation_id"]})
    require(r,409,lambda b:b.get("reason")=="STALE_REJECT","stale_generation_reject")
    run["stage"]="PREPARED"; run["prepared_at_utc"]=utc(); save(root,run)
    print(json.dumps({"result":"P347_MAC_ACTOR_PREPARED","run_id":rid,"run_dir":str(root),"actor_source_version":sha,
      "source_version":a.expected_source_version,"effect_id":eid,"mutation_disposition":run["mutation_disposition"]},sort_keys=True))
    return 0

def effect_once(a):
    root=Path(a.run_dir).expanduser().resolve(); run=load(root)
    if run.get("stage")!="PREPARED": raise RuntimeError("effect-once requires PREPARED stage")
    token=secret(a.effect_token_file); payload={"generation":2,"payload":{"amount":1}}
    r=call(root,run,"consequential_effect_first_attempt","POST","/v1/effects",token,payload,{"Idempotency-Key":run["effect_id"],
      "X-Request-Fingerprint":fingerprint(payload),"X-Correlation-ID":run["correlation_id"]},a.timeout_seconds)
    run["initial_effect_outcome"]="UNKNOWN" if r["transport_state"]=="UNKNOWN" else ("HTTP_RESPONSE_OBSERVED" if r["http_status"] in (200,201) else "HTTP_ERROR_OBSERVED")
    run["initial_effect_request"]={k:r.get(k) for k in ("request_started_utc","request_finished_utc","request_started_monotonic_ns",
      "request_finished_monotonic_ns","http_status","transport_state","local_ip","remote_ip","remote_port","response_body")}
    run["stage"]="EFFECT_ATTEMPTED"; run["effect_attempt_finished_at_utc"]=utc(); save(root,run)
    print(json.dumps({"result":"P347_MAC_ACTOR_EFFECT_ATTEMPT_RECORDED","run_id":run["run_id"],
      "initial_effect_outcome":run["initial_effect_outcome"],"http_status":r["http_status"],"local_ip":r["local_ip"],"remote_ip":r["remote_ip"]},sort_keys=True))
    return 0 # UNKNOWN is a knowledge state, not an inferred failure.

def reconcile(a):
    root=Path(a.run_dir).expanduser().resolve(); run=load(root)
    if run.get("stage")!="EFFECT_ATTEMPTED": raise RuntimeError("reconcile requires EFFECT_ATTEMPTED stage")
    token,eid=secret(a.effect_token_file),run["effect_id"]
    obs=call(root,run,"fresh_observation_before_retry","GET","/v1/effects/"+quote(eid,safe=""))
    if obs["transport_state"]=="UNKNOWN" or obs["http_status"] not in (200,404):
        run["stage"]="RECONCILIATION_UNKNOWN"; run["reconciliation_disposition"]="OBSERVATION_NOT_DECISIVE"; save(root,run)
        raise RuntimeError("fresh observation not decisive; stop before retry")
    present=obs["http_status"]==200; b=body(obs)
    if present and (b.get("effect_id")!=eid or b.get("generation")!=2 or b.get("payload")!={"amount":1}):
        raise RuntimeError("fresh observation conflicts with expected effect; stop before retry")
    original={"generation":2,"payload":{"amount":1}}
    h={"Idempotency-Key":eid,"X-Request-Fingerprint":fingerprint(original),"X-Correlation-ID":run["correlation_id"]}
    retry=call(root,run,"same_key_same_payload_reconciliation_retry","POST","/v1/effects",token,original,h,a.timeout_seconds)
    if retry["transport_state"]=="UNKNOWN":
        run["stage"]="RECONCILIATION_UNKNOWN"; run["reconciliation_disposition"]="RETRY_TRANSPORT_UNKNOWN"; save(root,run)
        raise RuntimeError("retry is UNKNOWN; preserve evidence and stop")
    rb=body(retry)
    retry_ok=(retry["http_status"]==200 and rb.get("duplicate") is True and rb.get("effect_id")==eid) if present else (retry["http_status"]==201 and rb.get("duplicate") is False and rb.get("effect_id")==eid)
    run["same_key_retry_pass"]=bool(retry_ok)
    conflict_payload={"generation":2,"payload":{"amount":2}}
    conflict=call(root,run,"same_key_different_payload_conflict","POST","/v1/effects",token,conflict_payload,{
      "Idempotency-Key":eid,"X-Request-Fingerprint":fingerprint(conflict_payload),"X-Correlation-ID":run["correlation_id"]},a.timeout_seconds)
    run["conflict_pass"]=conflict["http_status"]==409 and body(conflict).get("reason")=="CONFLICT"
    final=call(root,run,"fresh_effect_reobservation","GET","/v1/effects/"+quote(eid,safe="")); fb=body(final)
    run["fresh_reobservation_pass"]=final["http_status"]==200 and fb.get("effect_id")==eid and fb.get("generation")==2 and fb.get("payload")=={"amount":1} and fb.get("fingerprint")==h["X-Request-Fingerprint"]
    unknown=run.get("initial_effect_outcome")=="UNKNOWN"
    run["ambiguous_effect_recovery"]="VERIFIED_BOUNDED" if unknown and present and retry_ok and run["conflict_pass"] and run["fresh_reobservation_pass"] else "NOT_EXERCISED"
    run["claims"]["ambiguous_effect_recovery_verified"]=run["ambiguous_effect_recovery"]=="VERIFIED_BOUNDED"
    # Actor evidence alone cannot admit a lost ACK; that requires independent fault and packet-witness evidence.
    run["claims"]["lost_ack_exercised"]=False
    run["claims"]["physical_effect_admitted"]=False; run["claims"]["independent_witness_admitted"]=False
    run["result"]="PASS" if run["same_key_retry_pass"] and run["conflict_pass"] and run["fresh_reobservation_pass"] else "FAIL"
    run["stage"]="RECONCILED"; run["completed_at_utc"]=utc(); save(root,run)
    print(json.dumps({"result":run["result"],"run_id":run["run_id"],"same_key_retry_pass":run["same_key_retry_pass"],
      "conflict_pass":run["conflict_pass"],"fresh_reobservation_pass":run["fresh_reobservation_pass"],
      "ambiguous_effect_recovery":run["ambiguous_effect_recovery"],"physical_effect_admitted":False,"independent_witness_admitted":False,
      "evidence":str(root/"actor-evidence.json")},sort_keys=True))
    return 0 if run["result"]=="PASS" else 1

def main():
    p=argparse.ArgumentParser(description=__doc__); sub=p.add_subparsers(dest="cmd",required=True)
    x=sub.add_parser("prepare"); x.add_argument("--authority-url-file",default=str(SECRET_DIR/"authority-url"))
    x.add_argument("--admin-token-file",default=str(SECRET_DIR/"admin-token")); x.add_argument("--effect-token-file",default=str(SECRET_DIR/"effect-token"))
    x.add_argument("--expected-source-version",required=True); x.add_argument("--run-dir",required=True); x.set_defaults(fn=prepare)
    x=sub.add_parser("effect-once"); x.add_argument("--effect-token-file",default=str(SECRET_DIR/"effect-token"))
    x.add_argument("--run-dir",required=True); x.add_argument("--timeout-seconds",type=float,default=3.0); x.set_defaults(fn=effect_once)
    x=sub.add_parser("reconcile"); x.add_argument("--effect-token-file",default=str(SECRET_DIR/"effect-token"))
    x.add_argument("--run-dir",required=True); x.add_argument("--timeout-seconds",type=float,default=20.0); x.set_defaults(fn=reconcile)
    a=p.parse_args()
    try: return a.fn(a)
    except Exception as e: print("P347_MAC_ACTOR_ERROR="+type(e).__name__+": "+str(e),file=sys.stderr); return 2
if __name__=="__main__": raise SystemExit(main())
