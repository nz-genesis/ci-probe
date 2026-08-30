"""Clean-room differential reduction for authenticated external realization.

Generic experiment only. It compares three progressively stronger boundary models
and asks which added property closes which bounded adversarial distinction.
No private Genesis hypotheses, credentials, datasets, endpoints, or decisions.
"""

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class Envelope:
    request_id: str
    operation: str
    value: str
    admission: str
    provenance: str
    nonce: str | None = None
    effect_binding: str | None = None


def provenance(request_id: str, operation: str, value: str, admission: str) -> str:
    raw = "|".join((request_id, operation, value, admission)).encode()
    return sha256(raw).hexdigest()


def e1() -> Envelope:
    return Envelope("r1", "set", "v1", "allow", provenance("r1", "set", "v1", "allow"))


def e2() -> Envelope:
    base = e1()
    return Envelope(base.request_id, base.operation, base.value, base.admission, base.provenance, nonce="n1")


def e3() -> Envelope:
    base = e2()
    effect = sha256(f"{base.request_id}|effect|v1".encode()).hexdigest()
    return Envelope(base.request_id, base.operation, base.value, base.admission, base.provenance, base.nonce, effect)


def accept(e: Envelope, seen: set[str], require_effect: bool = False) -> str:
    if e.admission != "allow":
        return "rejected"
    if e.request_id + ":" + e.provenance in seen:
        return "replay"
    if require_effect and not e.effect_binding:
        return "missing-effect-binding"
    seen.add(e.request_id + ":" + e.provenance)
    return "accepted"


def main() -> None:
    # E1: authenticity/provenance can distinguish request substitution, but the
    # model has no freshness discriminator and no post-effect binding.
    base = e1()
    assert base.provenance == provenance(base.request_id, base.operation, base.value, base.admission)
    assert accept(base, set()) == "accepted"
    forged = Envelope(base.request_id, base.operation, base.value, "deny", base.provenance)
    assert accept(forged, set()) == "rejected"

    # E2: freshness/replay state is an independent requirement; a valid
    # envelope remains valid cryptographically but is rejected on second use.
    fresh = e2()
    seen: set[str] = set()
    assert accept(fresh, seen) == "accepted"
    assert accept(fresh, seen) == "replay"

    # E3: post-effect binding is independently required for evidence/effect
    # correspondence. Its presence is not inferred from authentication.
    bound = e3()
    assert accept(bound, set(), require_effect=True) == "accepted"
    unbound = Envelope(bound.request_id, bound.operation, bound.value, bound.admission, bound.provenance, bound.nonce)
    assert accept(unbound, set(), require_effect=True) == "missing-effect-binding"

    # Primitive-removal observation: the three properties answer different
    # adversarial questions, so they cannot be collapsed merely by naming them
    # all "execution security". This experiment does not assert they must become
    # Genesis primitives; it only records the tested semantic distinctions.
    print("external realization envelope differential reduction: PASS")
    print("E1=authenticated_provenance")
    print("E2=E1+replay_state")
    print("E3=E2+effect_binding")
    print("primitive_removal=NO_COLLAPSE_WITHIN_TESTED_ATTACKS")


if __name__ == "__main__":
    main()
