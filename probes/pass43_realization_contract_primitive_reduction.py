"""Pass 43: reduce realization-contract semantics against existing Genesis basis."""
from dataclasses import dataclass
from enum import Enum

class Decision(str, Enum):
    ALLOW = "ALLOW"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"
    HITL_REQUIRED = "HITL_REQUIRED"

@dataclass(frozen=True)
class Capability:
    subject: str
    action: str

@dataclass(frozen=True)
class Authority:
    subject: str
    action: str
    active: bool

@dataclass(frozen=True)
class Constraint:
    effect_class: str
    max_risk: int

@dataclass(frozen=True)
class Evidence:
    claim: str
    source: str
    valid: bool

@dataclass(frozen=True)
class RealizationContract:
    name: str
    supports_effect_class: str
    max_risk: int
    provenance: Evidence
    active: bool

def decide(capability, authority, constraint, contract, observations):
    if capability.subject != authority.subject or capability.action != authority.action:
        return Decision.REJECT
    if not authority.active:
        return Decision.REJECT
    if not constraint:
        return Decision.REJECT
    if not contract.active or not contract.provenance.valid:
        return Decision.HITL_REQUIRED
    if contract.supports_effect_class != constraint.effect_class:
        return Decision.HITL_REQUIRED
    if contract.max_risk < constraint.max_risk:
        return Decision.HITL_REQUIRED
    if observations == {"happened", "not_happened"}:
        return Decision.CONFLICT
    if observations == {"unknown"}:
        return Decision.UNKNOWN
    return Decision.ALLOW

def run():
    cap = Capability("alice", "pay")
    auth = Authority("alice", "pay", True)
    constraint = Constraint("irreversible", 3)
    good = RealizationContract("strong", "irreversible", 3, Evidence("supports irreversible", "cert-A", True), True)
    weak = RealizationContract("weak", "irreversible", 2, Evidence("supports irreversible", "cert-B", True), True)
    forged = RealizationContract("forged", "irreversible", 3, Evidence("supports irreversible", "attacker", False), True)
    revoked = RealizationContract("revoked", "irreversible", 3, Evidence("supports irreversible", "cert-C", True), False)
    assert decide(cap, auth, constraint, good, set()) == Decision.ALLOW
    assert decide(cap, auth, constraint, weak, set()) == Decision.HITL_REQUIRED
    assert decide(cap, auth, constraint, forged, set()) == Decision.HITL_REQUIRED
    assert decide(cap, auth, constraint, revoked, set()) == Decision.HITL_REQUIRED
    assert decide(cap, auth, constraint, good, {"unknown"}) == Decision.UNKNOWN
    assert decide(cap, auth, constraint, good, {"happened", "not_happened"}) == Decision.CONFLICT
    assert decide(Capability("mallory", "pay"), auth, constraint, good, set()) == Decision.REJECT
    assert decide(cap, Authority("alice", "pay", False), constraint, good, set()) == Decision.REJECT
    assert decide(cap, auth, Constraint("irreversible", 4), good, set()) == Decision.HITL_REQUIRED
    metadata_only = RealizationContract("claims-authority", "irreversible", 99, Evidence("alice authorized", "realizer", True), True)
    assert decide(Capability("mallory", "pay"), auth, constraint, metadata_only, set()) == Decision.REJECT
    print("PASS43_PUBLIC: PASS; cases=10")

if __name__ == "__main__":
    run()
