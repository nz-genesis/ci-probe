"""Pass 43: reduce realization-contract semantics against existing Genesis basis.

The realization contract is intentionally NOT a new semantic type here. Its
public representation is a composition of existing candidate primitives:
Capability + Constraint + Evidence, while Authority remains independent.
"""
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
    active: bool = True

@dataclass(frozen=True)
class Evidence:
    claim: str
    source: str
    valid: bool


def decide(actor_capability, authority, execution_constraint, realization_capability,
           realization_constraint, provenance, observations):
    if actor_capability.subject != authority.subject or actor_capability.action != authority.action:
        return Decision.REJECT
    if not authority.active:
        return Decision.REJECT
    if not execution_constraint.active or not realization_constraint.active:
        return Decision.HITL_REQUIRED
    if not provenance.valid:
        return Decision.HITL_REQUIRED
    if realization_capability.action != actor_capability.action:
        return Decision.HITL_REQUIRED
    if realization_constraint.effect_class != execution_constraint.effect_class:
        return Decision.HITL_REQUIRED
    if realization_constraint.max_risk < execution_constraint.max_risk:
        return Decision.HITL_REQUIRED
    if observations == {"happened", "not_happened"}:
        return Decision.CONFLICT
    if observations == {"unknown"}:
        return Decision.UNKNOWN
    return Decision.ALLOW


def run():
    actor = Capability("alice", "pay")
    auth = Authority("alice", "pay", True)
    execution = Constraint("irreversible", 3)
    strong_cap = Capability("realizer-A", "pay")
    strong_limit = Constraint("irreversible", 3)
    weak_cap = Capability("realizer-B", "pay")
    weak_limit = Constraint("irreversible", 2)
    valid = Evidence("supports irreversible pay", "cert-A", True)
    forged = Evidence("supports irreversible pay", "attacker", False)

    assert decide(actor, auth, execution, strong_cap, strong_limit, valid, set()) == Decision.ALLOW
    assert decide(actor, auth, execution, weak_cap, weak_limit, valid, set()) == Decision.HITL_REQUIRED
    assert decide(actor, auth, execution, strong_cap, strong_limit, forged, set()) == Decision.HITL_REQUIRED
    assert decide(actor, auth, execution, strong_cap, Constraint("irreversible", 3, False), valid, set()) == Decision.HITL_REQUIRED
    assert decide(actor, auth, execution, strong_cap, strong_limit, valid, {"unknown"}) == Decision.UNKNOWN
    assert decide(actor, auth, execution, strong_cap, strong_limit, valid, {"happened", "not_happened"}) == Decision.CONFLICT
    assert decide(Capability("mallory", "pay"), auth, execution, strong_cap, strong_limit, valid, set()) == Decision.REJECT
    assert decide(actor, Authority("alice", "pay", False), execution, strong_cap, strong_limit, valid, set()) == Decision.REJECT
    assert decide(actor, auth, Constraint("irreversible", 4), strong_cap, strong_limit, valid, set()) == Decision.HITL_REQUIRED
    # Removal/authority-laundering test: realizer metadata cannot manufacture actor authority.
    claims_authority = Evidence("alice authorized mallory", "realizer", True)
    assert decide(Capability("mallory", "pay"), auth, execution, Capability("realizer-X", "pay"), strong_limit, claims_authority, set()) == Decision.REJECT
    print("PASS43_PUBLIC: PASS; cases=10")

if __name__ == "__main__":
    run()
