#!/usr/bin/env python3
"""Independent P347 packet witness; no semantic inference."""
from __future__ import annotations
import argparse, hashlib, json, os, shutil, signal, socket, subprocess, time
from datetime import datetime, timezone
from pathlib import Path

def utc_now(): return datetime.now(timezone.utc).isoformat()
def append_event(path,event,**fields):
    r={"event":event,"wall_time_utc":utc_now(),"monotonic_ns":time.monotonic_ns(),
       "pid":os.getpid(),**fields}
    with path.open("a",encoding="utf-8") as f:
        f.write(json.dumps(r,sort_keys=True)+"\n"); f.flush(); os.fsync(f.fileno())
def sha256(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024),b""): h.update(chunk)
    return h.hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--interface",required=True)
    ap.add_argument("--capture-dir",required=True)
    ap.add_argument("--target-host",required=True)
    ap.add_argument("--target-port",type=int,default=443)
    ap.add_argument("--duration",type=int,default=300)
    a=ap.parse_args()
    out=Path(a.capture_dir).expanduser().resolve(); out.mkdir(parents=True,exist_ok=True)
    events=out/"witness-events.jsonl"; pcap=out/"witness.pcap"; meta=out/"witness-meta.json"
    ips=sorted({r[4][0] for r in socket.getaddrinfo(a.target_host,a.target_port,type=socket.SOCK_STREAM)})
    if not ips: raise RuntimeError("target host did not resolve")
    append_event(events,"capture_start",interface=a.interface,target_host=a.target_host,
                 target_port=a.target_port,target_ips=ips,duration_seconds=a.duration)
    tcpdump=shutil.which("tcpdump")
    if tcpdump is None: raise RuntimeError("tcpdump is required")
    host_filter=" or ".join(f"host {ip}" for ip in ips)
    cmd=[tcpdump,"-i",a.interface,"-nn","-s","0","-w",str(pcap),f"({host_filter})","and",f"port {a.target_port}"]
    stderr_path=out/"tcpdump-stderr.txt"
    stderr_file=stderr_path.open("w",encoding="utf-8")
    proc=subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=stderr_file,text=True)
    try: time.sleep(a.duration)
    finally:
        proc.send_signal(signal.SIGINT)
        try: proc.wait(timeout=10)
        except subprocess.TimeoutExpired: proc.kill(); proc.wait(timeout=5)
        finally: stderr_file.close()
    append_event(events,"capture_stop",returncode=proc.returncode)
    if proc.returncode not in (0, 130):
        raise RuntimeError(f"tcpdump failed with return code {proc.returncode}; see {stderr_path}")
    if not pcap.exists() or pcap.stat().st_size < 24:
        raise RuntimeError("tcpdump produced no valid pcap")
    meta.write_text(json.dumps({"schema":"p347-n100-witness-v1","host":socket.gethostname(),
        "interface":a.interface,"target_host":a.target_host,"target_port":a.target_port,
        "target_ips":ips,"tcpdump_filter":"host("+" or ".join(ips)+f") and port {a.target_port}","pcap_sha256":sha256(pcap),"events_sha256":sha256(events),"tcpdump_stderr_sha256":sha256(stderr_path)},indent=2,sort_keys=True)+"\n")
    print(f"pcap={pcap}\npcap_sha256={sha256(pcap)}\nevents_sha256={sha256(events)}")
if __name__=="__main__": raise SystemExit(main())
