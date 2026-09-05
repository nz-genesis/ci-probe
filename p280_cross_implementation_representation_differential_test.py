import hashlib
import json
from dataclasses import dataclass


@dataclass(frozen=True)
class Transition:
    state_digest: str
    target: str
    epoch: int
    authority_digest: str
    operation: str


def encode_a(t: Transition) -> bytes:
    obj = {"state_digest": t.state_digest, "target": t.target, "epoch": t.epoch, "authority_digest": t.authority_digest, "operation": t.operation}
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def encode_b(t: Transition) -> bytes:
    parts = [
        ("authority_digest", json.dumps(t.authority_digest, ensure_ascii=False, separators=(",", ":"))),
        ("epoch", str(t.epoch)),
        ("operation", json.dumps(t.operation, ensure_ascii=False, separators=(",", ":"))),
        ("state_digest", json.dumps(t.state_digest, ensure_ascii=False, separators=(",", ":"))),
        ("target", json.dumps(t.target, ensure_ascii=False, separators=(",", ":"))),
    ]
    return ("{" + ",".join(json.dumps(k) + ":" + v for k, v in parts) + "}").encode("utf-8")


def digest(domain: str, payload: bytes) -> str:
    return hashlib.sha256(domain.encode("ascii") + b"\x00" + payload).hexdigest()


def _reject_duplicates(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("duplicate key")
        out[key] = value
    return out


def strict_decode(raw: bytes) -> Transition:
    text = raw.decode("utf-8")
    pairs = json.loads(text, object_pairs_hook=_reject_duplicates)
    required = {"state_digest", "target", "epoch", "authority_digest", "operation"}
    if set(pairs) != required or type(pairs["epoch"]) is not int:
        raise ValueError("schema/type mismatch")
    if not all(type(pairs[k]) is str for k in ("state_digest", "target", "authority_digest", "operation")):
        raise ValueError("field type mismatch")
    return Transition(pairs["state_digest"], pairs["target"], pairs["epoch"], pairs["authority_digest"], pairs["operation"])


def rejects(raw: bytes) -> None:
    try:
        strict_decode(raw)
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError):
        return
    raise AssertionError("non-canonical representation was accepted")


def run() -> None:
    t = Transition("S1", "Genesis", 7, "A7", "self-change")
    domain = "genesis.transition.v1"
    a, b = encode_a(t), encode_b(t)

    assert a == b
    signed = digest(domain, a)
    assert digest(domain, b) == signed
    assert strict_decode(a) == t and strict_decode(b) == t

    changed = Transition("S1", "Other", 7, "A7", "self-change")
    assert digest(domain, encode_a(changed)) != signed
    assert digest("genesis.authority.v1", a) != signed

    rejects(b'{"authority_digest":"A7","epoch":7,"epoch":8,"operation":"self-change","state_digest":"S1","target":"Genesis"}')
    rejects(b'{"authority_digest":"A7","epoch":7.0,"operation":"self-change","state_digest":"S1","target":"Genesis"}')
    rejects(b'{"authority_digest":"A7","epoch":"7","operation":"self-change","state_digest":"S1","target":"Genesis"}')
    rejects(b'{"authority_digest":"A7","epoch":7,"operation":"self-change","state_digest":"S1"}')
    rejects(b'{"authority_digest":"A7","epoch":7,"operation":"self-change","state_digest":"S1","target":"Genesis","admin":true}')

    unicode_t = Transition("S1", "Ж", 7, "A7", "self-change")
    assert encode_a(unicode_t) == encode_b(unicode_t)
    assert strict_decode(encode_a(unicode_t)) == unicode_t

    rejects(b'{"authority_digest":"A7","epoch":7,"operation":"self-change","state_digest":"S1","target":"Genesis"')
    rejects(b'not-json')

    print("P280 cross-implementation representation differential: 12/12 PASS")


if __name__ == "__main__":
    run()
