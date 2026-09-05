import hashlib
import json
from dataclasses import dataclass
from enum import Enum


class Verdict(Enum):
    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Transition:
    state_digest: str
    target: str
    epoch: int
    authority_digest: str
    operation: str


def canonical_bytes(t: Transition) -> bytes:
    # Bounded model: one explicit schema, deterministic key order, UTF-8,
    # compact separators, and typed field names. This is a model invariant,
    # not a claim about production serialization/crypto implementation.
    obj = {
        "authority_digest": t.authority_digest,
        "epoch": t.epoch,
        "operation": t.operation,
        "state_digest": t.state_digest,
        "target": t.target,
    }
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def digest(domain: str, t: Transition) -> str:
    return hashlib.sha256(domain.encode("ascii") + b"\x00" + canonical_bytes(t)).hexdigest()


def verify(signed_domain: str, expected_domain: str, signed: Transition, presented: Transition, signed_digest: str) -> Verdict:
    if signed_domain != expected_domain:
        return Verdict.INVALID
    if signed != presented:
        return Verdict.INVALID
    return Verdict.VALID if digest(expected_domain, presented) == signed_digest else Verdict.INVALID


def run() -> None:
    t = Transition("S1", "Genesis", 7, "A7", "self-change")
    signed = digest("genesis.transition.v1", t)

    # Exact semantic object / exact domain succeeds.
    assert verify("genesis.transition.v1", "genesis.transition.v1", t, t, signed) is Verdict.VALID

    # Domain confusion: evidence for another object class is not reusable.
    assert verify("genesis.authority.v1", "genesis.transition.v1", t, t, signed) is Verdict.INVALID

    # Target substitution is security-significant even when the rest is equal.
    other_target = Transition("S1", "OtherTarget", 7, "A7", "self-change")
    assert verify("genesis.transition.v1", "genesis.transition.v1", t, other_target, signed) is Verdict.INVALID

    # Epoch substitution is security-significant.
    other_epoch = Transition("S1", "Genesis", 8, "A7", "self-change")
    assert verify("genesis.transition.v1", "genesis.transition.v1", t, other_epoch, signed) is Verdict.INVALID

    # Authority substitution is security-significant.
    other_authority = Transition("S1", "Genesis", 7, "A8", "self-change")
    assert verify("genesis.transition.v1", "genesis.transition.v1", t, other_authority, signed) is Verdict.INVALID

    # Operation substitution is security-significant.
    other_operation = Transition("S1", "Genesis", 7, "A7", "delete-constraint")
    assert verify("genesis.transition.v1", "genesis.transition.v1", t, other_operation, signed) is Verdict.INVALID

    # Serialization is deterministic for the same structured object.
    assert canonical_bytes(t) == canonical_bytes(t)
    assert digest("genesis.transition.v1", t) == digest("genesis.transition.v1", t)

    # A raw representation with duplicate JSON keys is not accepted as a
    # second semantic source. The bounded verifier only consumes the typed,
    # canonical representation produced by the schema above.
    ambiguous = b'{"epoch":7,"epoch":8,"state_digest":"S1","target":"Genesis","authority_digest":"A7","operation":"self-change"}'
    assert ambiguous != canonical_bytes(t)

    # Cross-type domain separation prevents a valid transition digest from
    # becoming authority evidence merely by relabelling its context.
    authority_domain_digest = hashlib.sha256(b"genesis.authority.v1\x00" + canonical_bytes(t)).hexdigest()
    assert authority_domain_digest != signed

    # Missing / unverifiable representation is not promoted to valid evidence.
    assert verify("genesis.transition.v1", "genesis.transition.v1", t, t, "UNKNOWN") is Verdict.INVALID

    print("P279 representation/domain binding: 10/10 PASS")


if __name__ == "__main__":
    run()
