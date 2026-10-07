#!/usr/bin/env python3
import hashlib, json, sys
def canon(v): return json.dumps(v,sort_keys=True,separators=(",",":"))
pending=None
consumed=set()
for raw in sys.stdin:
    m=json.loads(raw)
    if m.get("type")=="signal":
        rid=m["request_id"]; options=m["options"]
        cid="cl-"+hashlib.sha256((rid+"|"+canon(options)).encode()).hexdigest()[:24]
        pending=(rid,cid,options)
        out={"type":"clarification_required","request_id":rid,"clarification_id":cid,"options":options}
    elif m.get("type")=="clarification_response":
        if pending is None: out={"status":"NO_PENDING_CLARIFICATION"}
        else:
            rid,cid,options=pending
            if m.get("request_id")!=rid or m.get("clarification_id")!=cid:
                out={"status":"STALE_OR_MISMATCHED_RESPONSE"}
            elif any(k in m for k in ("authority","capability","grant","allow","role")):
                out={"status":"AUTHORITY_INJECTION_REJECTED"}
            elif cid in consumed:
                out={"status":"REPLAYED_RESPONSE"}
            elif not isinstance(m.get("selected_index"),int) or not 0<=m["selected_index"]<len(options):
                out={"status":"INVALID_SELECTION"}
            else:
                consumed.add(cid); selected=options[m["selected_index"]]
                pending=None
                out={"type":"executed","request_id":rid,"clarification_id":cid,"selected_index":m["selected_index"],"value":selected["value"]}
    else:
        out={"type":"protocol_error"}
    sys.stdout.write(json.dumps(out,sort_keys=True)+"\n"); sys.stdout.flush()
