import hashlib
import json
import subprocess


TRANSITION = {
    "state_digest": "S1",
    "target": "Genesis",
    "epoch": 7,
    "authority_digest": "A7",
    "operation": "self-change",
}
DOMAIN = "genesis.transition.v1"


def canonical_python(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(payload):
    return hashlib.sha256(DOMAIN.encode("ascii") + b"\x00" + payload).hexdigest()


def node_encoder(value):
    script = r'''const fs = require("fs");
const x = JSON.parse(fs.readFileSync(0, "utf8"));
const keys = ["authority_digest", "epoch", "operation", "state_digest", "target"];
let s = "{";
for (let i = 0; i < keys.length; i++) {
  if (i) s += ",";
  const k = keys[i];
  s += JSON.stringify(k) + ":" + JSON.stringify(x[k], (_k, v) => v);
}
s += "}";
process.stdout.write(s);
'''
    p = subprocess.run(["node", "-e", script], input=json.dumps(value), text=True, capture_output=True, check=True)
    return p.stdout.encode("utf-8")


def rejects_node(raw):
    script = r'''const fs = require("fs");
const raw = fs.readFileSync(0, "utf8");
try {
  const x = JSON.parse(raw);
  const required = ["state_digest", "target", "epoch", "authority_digest", "operation"].sort();
  const got = Object.keys(x).sort();
  if (JSON.stringify(required) !== JSON.stringify(got) || !Number.isInteger(x.epoch)) process.exit(0);
  const canonical = "{" + ["authority_digest", "epoch", "operation", "state_digest", "target"].map(k => JSON.stringify(k)+":"+JSON.stringify(x[k])).join(",") + "}";
  if (raw === canonical) process.exit(1);
  process.exit(0);
} catch (_) { process.exit(0); }
'''
    p = subprocess.run(["node", "-e", script], input=raw.decode("utf-8"), text=True, capture_output=True)
    if p.returncode != 0:
        raise AssertionError("Node accepted non-canonical representation")


def run():
    py = canonical_python(TRANSITION)
    node = node_encoder(TRANSITION)
    assert py == node
    assert digest(py) == digest(node)

    for key, value in [("target", "Other"), ("epoch", 8), ("authority_digest", "A8"), ("operation", "other")]:
        changed = dict(TRANSITION)
        changed[key] = value
        assert digest(canonical_python(changed)) != digest(py)

    reordered = b'{"target":"Genesis","state_digest":"S1","operation":"self-change","epoch":7,"authority_digest":"A7"}'
    rejects_node(reordered)
    rejects_node(b'{"authority_digest":"A7","epoch":7,"epoch":8,"operation":"self-change","state_digest":"S1","target":"Genesis"}')
    rejects_node(b'{"authority_digest":"A7","epoch":7.0,"operation":"self-change","state_digest":"S1","target":"Genesis"}')
    rejects_node(b'{"authority_digest":"A7","epoch":"7","operation":"self-change","state_digest":"S1","target":"Genesis"}')
    rejects_node(b'{"authority_digest":"A7","epoch":7,"operation":"self-change","state_digest":"S1","target":"Genesis","admin":true}')

    unicode_value = dict(TRANSITION, target="Ж")
    assert canonical_python(unicode_value) == node_encoder(unicode_value)

    # Domain separation must survive the runtime boundary.
    assert hashlib.sha256(b"genesis.transition.v1\x00" + py).hexdigest() != hashlib.sha256(b"genesis.authority.v1\x00" + py).hexdigest()

    print("P281 cross-runtime representation differential: 11/11 PASS")


if __name__ == "__main__":
    run()
