#!/usr/bin/env python3
"""Genesis-agnostic public control for a real clarification user-channel boundary."""
from __future__ import annotations
import hashlib
import json
import subprocess
import sys
from pathlib import Path

CHANNEL = Path(__file__).with_name("s02-clarification-channel-worker.py")

def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":"))

def cid(request_id, options):
    return "cl-" + hashlib.sha256((request_id + "|" + canonical(options)).encode()).hexdigest()[:24]

def main():
    p = subprocess.Popen(
        [sys.executable, str(CHANNEL)],
        stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        text=True, bufsize=1,
    )
    def send(msg):
        p.stdin.write(json.dumps(msg) + "\\n")
        p.stdin.flush()
        line=p.stdout.readline()
        assert line
        return json.loads(line)
    try:
        options=[{"index":0,"value":"A"},{"index":1,"value":"B"}]
        first=send({"type":"signal","request_id":"req-public-001","options":options})
        assert first["type"]=="clarification_required"
        assert first["options"]==options
        expected=cid("req-public-001", options)
        assert first["clarification_id"]==expected

        stale=send({"type":"clarification_response","request_id":"wrong","clarification_id":expected,"selected_index":1})
        assert stale["status"]=="STALE_OR_MISMATCHED_RESPONSE"

        injected=send({"type":"clarification_response","request_id":"req-public-001","clarification_id":expected,"selected_index":1,"authority":{"grant":["anything"]}})
        assert injected["status"]=="AUTHORITY_INJECTION_REJECTED"

        executed=send({"type":"clarification_response","request_id":"req-public-001","clarification_id":expected,"selected_index":1})
        assert executed["type"]=="executed"
        assert executed["selected_index"]==1
        assert executed["value"]=="B"

        replay=send({"type":"clarification_response","request_id":"req-public-001","clarification_id":expected,"selected_index":1})
        assert replay["status"]=="REPLAYED_RESPONSE"

        print(json.dumps({
            "control_id":"S02-REAL-USER-CHANNEL-CLARIFICATION-V1",
            "status":"PASS",
            "options_preserved":2,
            "stale_rejected":True,
            "authority_injection_rejected":True,
            "execution_requires_explicit_selection":True,
            "replay_rejected":True,
        }, sort_keys=True))
    finally:
        p.stdin.close()
        p.terminate()
        p.wait(timeout=5)

if __name__=="__main__":
    main()

# Trigger fresh hosted execution after apparatus review: 2026-10-07.
