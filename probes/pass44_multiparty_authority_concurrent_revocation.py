"""Pass 44: multi-party authority and concurrent revocation reduction.

No new Genesis primitive is introduced. A multi-party requirement is represented
as existing Authority records plus a Constraint over a Transition. The probe
checks that capability, evidence, realization claims, and concurrent revocation
cannot manufacture or preserve authority.
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
    epoch: int


@dataclass(frozen=True)
class Constraint:
    required_subjects: frozenset[str]
    active: bool = True


@dataclass(frozen=True)
class Evidence:
    claim: str
    source: str
    valid: bool
    epoch: int


def decide(capability, authorities, constraint, evidence, observed_epoch=None):
    if not constraint.active or not evidence.valid:
        return Decision.HITL_REQUIRED
    if capability.subject != "service" or capability.action != evidence.claim:
        return Decision.REJECT
    if not constraint.required_subjects.issubset({a.subject for a in authorities}):
        return Decision.REJECT
    active = {
        a.subject for a in authorities
        if a.active and a.action == capability.action and a.subject in constraint.required_subjects
    }
    if active != constraint.required_subjects:
        return Decision.REJECT
    if any(a.epoch != evidence.epoch for a in authorities if a.subject in constraint.required_subjects):
        return Decision.UNKNOWN
    if observed_epoch is not None and observed_epoch != evidence.epoch:
        return Decision.UNKNOWN
    return Decision.ALLOW


def validate_substitution(original, candidate):
    """A contract substitution that changes required authorities is not silent."""
    if not candidate.active:
        return Decision.HITL_REQUIRED
    if candidate.required_subjects != original.required_subjects:
        return Decision.HITL_REQUIRED
    return Decision.ALLOW


def run():
    action = "approve"
    cap = Capability("service", action)
    constraint = Constraint(frozenset({"alice", "bob"}))
    authorities = [
        Authority("alice", action, True, 7),
        Authority("bob", action, True, 7),
        Authority("carol", action, True, 7),
    ]
    evidence = Evidence(action, "authority-registry", True, 7)

    assert decide(cap, authorities, constraint, evidence) == Decision.ALLOW

    revoked_bob = [authorities[0], Authority("bob", action, False, 8), authorities[2]]
    assert decide(cap, revoked_bob, constraint, evidence) == Decision.REJECT
    assert decide(cap, [authorities[0], authorities[2]], constraint, evidence) == Decision.REJECT

    fresh_after_revocation = Evidence(action, "authority-registry", True, 8)
    assert decide(cap, revoked_bob, constraint, fresh_after_revocation) == Decision.REJECT

    revoked_carol = [authorities[0], authorities[1], Authority("carol", action, False, 8)]
    assert decide(cap, revoked_carol, constraint, evidence) == Decision.ALLOW

    assert decide(Capability("mallory", action), authorities, constraint, evidence) == Decision_REJECT

    forged = Evidence(action, "realizer-claims-alice-and-bob", True, 7)
    missing_bob = [authorities[0], authorities[2]]
    assert decide(cap, missing_bob, constraint, forged) == Decision_REJECT

    assert decide(cap, authorities, constraint, evidence, observed_epoch=8) == Decision_UNKNOWN

    narrowed = Constraint(frozenset({"alice"}))
    widened = Constraint(frozenset({"alice", "bob", "carol"}))
    assert validate_substitution(constraint, narrowed) == Decision_HITL_REQUIRED
    assert validate_substitution(constraint, widened) == Decision_HITL_REQUIRED

    assert all(not name.endswith("MultiPartyAuthority") for name in globals())

    print("PASS44_PUBLIC: PASS; cases=10")


Decision_REJECT = Decision.REJECT
Decision_UNKNOWN = Decision.UNKNOWN
Decision_HITL_REQUIRED = Decision.HITL_REQUIRED


if __name__ == "__main__":
    run()
