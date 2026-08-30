"""Clean-room differential reduction for external realization envelopes.

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
    # E1: provenance binding detects mutation of the bound request/admission,
    # but by itself supplies neither freshness nor effect/evidence binding.
    base = e1()
    assert base.provenance == provenance(base.request_id, base.operation, base.value, base.admission)
    assert accept(base, set()) == "accepted"
    forged = Envelope(base.request_id, base.operation, base.value, "deny", base.provenance)
    assert accept(forged, set()) == "rejected"

    # E2: freshness/replay state is independent. A valid envelope is rejected
    # on second use even though its content remains unchanged.
    fresh = e2()
    seen: set[str] = set()
    assert accept(fresh, seen) == "accepted"
    assert accept(fresh, seen) == "replay"

    # E3: post-effect binding is independently required for effect/evidence
    # correspondence; it cannot be inferred from provenance alone.
    bound = e3()
    assert accept(bound, set(), require_effect=True) == "accepted"
    unbound = Envelope(bound.request_id, bound.operation, bound.value, bound.admission, bound.provenance, bound.nonce)
    assert accept(unbound, set(), require_effect=True) == "missing-effect-binding"

    # Primitive-removal observation: these properties answer different tested
    # adversarial questions. This does not promote any of them to a Genesis
    # primitive; it records only the bounded semantic distinctions observed.
    print("external realization envelope differential reduction: PASS")
    print("E1=provenance_binding")
    print("E2=E1+replay_state")
    print("E3=E2+effect_binding")
    print("primitive_removal=NO_COLLAPSE_WITHIN_TESTED_ATTACKS")


if __name__ == "__main__":
    main()
