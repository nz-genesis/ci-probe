import hashlib
import json
import subprocess

DOMAIN = "genesis.transition.v1"
KEYS = ["authority_digest", "epoch", "operation", "state_digest", "target"]


def py_encode(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def node_encode(value):
    script = r'''const fs=require("fs");
const x=JSON.parse(fs.readFileSync(0,"utf8"));
const keys=["authority_digest","epoch","operation","state_digest","target"];
process.stdout.write("{"+keys.map(k=>JSON.stringify(k)+":"+JSON.stringify(x[k])).join(",")+"}");'''
    p = subprocess.run(["node", "-e", script], input=json.dumps(value), text=True, capture_output=True, check=True)
    return p.stdout.encode("utf-8")


def d(raw):
    return hashlib.sha256(DOMAIN.encode()+b"\x00"+raw).hexdigest()


def run():
    base = {"state_digest":"S1","target":"Genesis","epoch":7,"authority_digest":"A7","operation":"self-change"}
    assert py_encode(base) == node_encode(base)

    # IEEE-754 boundary: JSON numbers above 2^53 are not exactly representable in JS.
    boundary = dict(base, epoch=9007199254740991)
    assert py_encode(boundary) == node_encode(boundary)

    unsafe = dict(base, epoch=9007199254740993)
    py = py_encode(unsafe)
    node = node_encode(unsafe)
    assert py != node, "runtime differential was not exposed at unsafe integer boundary"
    assert d(py) != d(node)

    # A governed transition must reject a runtime-produced representation that
    # changes the exact integer value rather than silently accepting it.
    node_value = json.loads(node.decode())
    assert node_value["epoch"] == 9007199254740992
    assert node_value["epoch"] != unsafe["epoch"]

    # Negative and safe integer controls remain interoperable.
    for n in (-9007199254740991, -1, 0, 1, 9007199254740991):
        value = dict(base, epoch=n)
        assert py_encode(value) == node_encode(value)

    print("P282 numeric boundary runtime differential: 5/5 PASS")


if __name__ == "__main__":
    run()
