#!/usr/bin/env python3
"""Read-only Mac-side discovery for the P347/N100 topology visibility preflight."""
import argparse, hashlib, json, os, platform, re, subprocess, sys, time, uuid
from datetime import datetime, timezone
from pathlib import Path
from actor import request

TRANSIENT_EDGE={(404,1042),(500,1104)}

def utc():
    return datetime.now(timezone.utc).isoformat()

def sanitize_result(result):
    """Keep public artifacts useful without publishing Cloudflare challenge HTML/tokens."""
    result=dict(result)
    body=result.get("response_body")
    if isinstance(body,dict) and isinstance(body.get("raw"),str):
        raw=body["raw"]
        match=re.search(r"<title[^>]*>(.*?)</title>",raw,re.IGNORECASE|re.DOTALL)
        title=re.sub(r"\s+"," ",match.group(1)).strip()[:120] if match else None
        challenge=("Just a moment" in raw or "__cf_chl" in raw or "challenges.cloudflare.com" in raw)
        safe_preview=None
        # Preserve only short, plain-text diagnostic tokens with a strict safe alphabet.
        # Never preserve HTML, headers, credentials, URLs with query strings, or arbitrary bodies.
        candidate=raw.strip()
        if not challenge and re.fullmatch(r"[A-Za-z0-9 .,_:/-]{1,160}",candidate):
            safe_preview=candidate
        result["response_body"]={
            "raw_body_sha256":hashlib.sha256(raw.encode("utf-8",errors="replace")).hexdigest(),
            "raw_body_chars":len(raw),"raw_body_redacted":True,"page_title":title,
            "cloudflare_challenge_detected":challenge,
        }
        if safe_preview is not None:
            result["response_body"]["safe_body_preview"]=safe_preview
    return result


def write_evidence(path,evidence):
    path=Path(path).expanduser().resolve()
    path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_name(path.name+".tmp")
    with tmp.open("w",encoding="utf-8") as f:
        json.dump(evidence,f,ensure_ascii=False,indent=2,sort_keys=True)
        f.write("\n"); f.flush(); os.fsync(f.fileno())
    tmp.replace(path); path.chmod(0o600)

def transient(result):
    b=result.get("response_body")
    b=b if isinstance(b,dict) else {}
    s=result.get("http_status")
    return result.get("transport_state")=="UNKNOWN" or s==523 or (s,b.get("error_code")) in TRANSIENT_EDGE

def one_probe(url,expected_source,name,request_fn=request,sleep_fn=time.sleep,max_attempts=5):
    correlation_id=str(uuid.uuid4()); attempts=[]
    for attempt in range(1,max_attempts+1):
        r=sanitize_result(request_fn(url+"/v1/state",method="GET",headers={"X-Correlation-ID":correlation_id},timeout=10.0))
        r.update({"name":name,"attempt":attempt,"correlation_id":correlation_id})
        attempts.append(r); b=r.get("response_body"); b=b if isinstance(b,dict) else {}
        if r.get("http_status")==200 and r.get("transport_state")=="HTTP_RESPONSE_OBSERVED":
            if b.get("authority")!="P347_EXTERNAL_AUTHORITY": return attempts,r,False,"authority identity mismatch"
            if b.get("source_version")!=expected_source: return attempts,r,False,"authority source_version mismatch"
            if not r.get("local_ip") or not r.get("remote_ip"): return attempts,r,False,"curl did not report local_ip and remote_ip"
            return attempts,r,True,None
        if attempt<max_attempts and transient(r):
            sleep_fn(2); continue
        return attempts,r,False,"read-only state probe did not become valid"
    return attempts,attempts[-1],False,"bounded read-only probe budget exhausted"

def current_checkout_sha():
    root=Path(__file__).resolve().parents[2]
    p=subprocess.run(["git","rev-parse","HEAD"],cwd=root,capture_output=True,text=True,check=False)
    if p.returncode: raise RuntimeError("cannot establish exact actor checkout SHA")
    return p.stdout.strip()

def discover(a,request_fn=request,sleep_fn=time.sleep):
    url=Path(a.authority_url_file).expanduser().read_text(encoding="utf-8").strip().rstrip("/")
    if not url.startswith("https://") or ".workers.dev" not in url:
        raise RuntimeError("authority URL must be HTTPS workers.dev URL, not claim URL")
    actor_sha=current_checkout_sha()
    if actor_sha!=a.actor_source_version: raise RuntimeError("actor checkout SHA does not match triggering source SHA")
    e={"schema":"p347-mac-visibility-discovery-v1","run_id":os.environ.get("GITHUB_RUN_ID",str(uuid.uuid4())),
       "actor_source_version":actor_sha,"authority_source_version_expected":a.expected_source_version,
       "authority_url":url,"actor_host":platform.node(),"actor_platform":platform.platform(),
       "started_at_utc":utc(),"probes":[],"transient_retry_events":[],
       "witness_visibility":"PENDING_N100_CAPTURE_CORRELATION",
       "claims":{"n100_packet_visibility_admitted":False,"lost_ack_exercised":False}}
    attempts,initial,ok,error=one_probe(url,a.expected_source_version,"initial_remote_ip_discovery",request_fn,sleep_fn)
    e["initial_discovery"]={"attempts":attempts,"valid":ok,"error":error}; e["probes"].append(initial)
    for old in attempts[:-1]:
        e["transient_retry_events"].append({"probe":"initial_remote_ip_discovery","attempt":old.get("attempt"),
          "http_status":old.get("http_status"),"transport_state":old.get("transport_state"),"response_body":old.get("response_body")})
    if not ok:
        e["result"]="FAIL"; e["completed_at_utc"]=utc(); write_evidence(a.output,e)
        print(json.dumps({"result":"P347_MAC_VISIBILITY_DISCOVERY_FAIL","error":error,"evidence":a.output},sort_keys=True),flush=True)
        return 1
    e["mac_ip"]=initial["local_ip"]; e["authority_ips"]=[initial["remote_ip"]]
    e["capture_window"]={"opened_at_utc":utc(),"probe_delay_seconds":a.window_seconds,
      "recommended_capture_duration_seconds":max(240,a.window_seconds+120),"probe_count":a.probe_count}
    write_evidence(a.output,e)
    print(json.dumps({"event":"N100_CAPTURE_WINDOW_OPEN","run_id":e["run_id"],
      "actor_source_version":actor_sha,"authority_source_version":a.expected_source_version,"authority_url":url,
      "MAC_IP":e["mac_ip"],"AUTHORITY_IP":initial["remote_ip"],"PROBE_START_IN_SECONDS":a.window_seconds,
      "CAPTURE_DURATION_RECOMMENDED_SECONDS":e["capture_window"]["recommended_capture_duration_seconds"],
      "N100_CAPTURE_REQUIRED":True,"WITNESS_VISIBILITY":"PENDING_N100_CAPTURE_CORRELATION"},sort_keys=True),flush=True)
    sleep_fn(a.window_seconds)
    all_valid=True
    for index in range(1,a.probe_count+1):
        name="visibility_probe_"+str(index)
        attempts,result,valid,error=one_probe(url,a.expected_source_version,name,request_fn,sleep_fn)
        e["probes"].append(result); e.setdefault("probe_attempts",[]).append({"name":name,"attempts":attempts,"valid":valid,"error":error})
        for old in attempts[:-1]:
            e["transient_retry_events"].append({"probe":name,"attempt":old.get("attempt"),"http_status":old.get("http_status"),
              "transport_state":old.get("transport_state"),"response_body":old.get("response_body")})
        if result.get("remote_ip") and result["remote_ip"] not in e["authority_ips"]: e["authority_ips"].append(result["remote_ip"])
        if not valid: all_valid=False
        print(json.dumps({"event":"MAC_VISIBILITY_PROBE","probe":name,"valid":valid,"error":error,
          "http_status":result.get("http_status"),"local_ip":result.get("local_ip"),"remote_ip":result.get("remote_ip"),
          "request_started_utc":result.get("request_started_utc"),"request_finished_utc":result.get("request_finished_utc"),
          "correlation_id":result.get("correlation_id")},sort_keys=True),flush=True)
        write_evidence(a.output,e)
        if index<a.probe_count: sleep_fn(2)
    e["capture_window"]["closed_at_utc"]=utc(); e["completed_at_utc"]=utc()
    e["result"]="PASS" if all_valid else "FAIL"
    # Mac-only discovery cannot admit N100 visibility or a physical lost ACK.
    e["witness_visibility"]="PENDING_N100_CAPTURE_CORRELATION"
    e["claims"]["n100_packet_visibility_admitted"]=False; e["claims"]["lost_ack_exercised"]=False
    write_evidence(a.output,e)
    print(json.dumps({"result":"P347_MAC_VISIBILITY_DISCOVERY_"+e["result"],"run_id":e["run_id"],
      "mac_ip":e["mac_ip"],"authority_ips":e["authority_ips"],"probe_count":a.probe_count,
      "witness_visibility":e["witness_visibility"],"evidence":a.output},sort_keys=True),flush=True)
    return 0 if all_valid else 1

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--authority-url-file",required=True); p.add_argument("--expected-source-version",required=True)
    p.add_argument("--actor-source-version",required=True); p.add_argument("--output",required=True)
    p.add_argument("--window-seconds",type=int,default=120); p.add_argument("--probe-count",type=int,default=3)
    a=p.parse_args()
    if a.window_seconds<0 or not 1<=a.probe_count<=10: p.error("window-seconds must be >= 0 and probe-count must be 1..10")
    try: return discover(a)
    except Exception as exc:
        print("P347_MAC_VISIBILITY_ERROR="+type(exc).__name__+": "+str(exc),file=sys.stderr); return 2
if __name__=="__main__": raise SystemExit(main())
