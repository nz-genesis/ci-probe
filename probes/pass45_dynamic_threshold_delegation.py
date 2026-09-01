"""Pass 45: dynamic k-of-n authority and delegation reduction.

Bounded experiment: threshold requirements, membership changes, revocation and
bounded delegation are represented with Authority + Constraint + Evidence.
Delegation cannot widen action scope or resurrect revoked authority. No new
Genesis primitive is introduced.
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
class Authority:
    subject: str
    action: str
    active: bool
    epoch: int
    delegator: str | None = None


@dataclass(frozen=True)
class Constraint:
    threshold: int
    eligible: frozenset[str]
    active: bool = True


@dataclass(frozen=True)
class Evidence:
    claim: str
    epoch: int
    valid: bool
    source: str


def decide(action, authorities, constraint, evidence, observed_epoch=None):
    if not constraint.active or not evidence.valid:
        return Decision.HITL_REQUIRED
    if evidence.claim != action:
        return Decision.REJECT
    if constraint.threshold < 1 or constraint.threshold > len(constraint.eligible):
        return Decision.HITL_REQUIRED
    if observed_epoch is not None and observed_epoch != evidence.epoch:
        return Decision.UNKNOWN

    eligible_active = {
        a.subject for a in authorities
        if a.action == action
        and a.active
        and a.subject in constraint.eligible
        and a.epoch == evidence.epoch
    }
    if len(eligible_active) >= constraint.threshold:
        return Decision.ALLOW
    return Decision.REJECT


def validate_delegation(parent, child):
    """A delegation preserves parent action/epoch scope and cannot resurrect it."""
    if not parent.active or not child.active:
        return Decision.REJECT
    if child.delegator != parent.subject:
        return Decision.REJECT
    if child.action != parent.action:
        return Decision.REJECT
    if child.epoch != parent.epoch:
        return Decision.UNKNOWN
    return Decision.ALLOW


def validate_chain(chain):
    """Every edge must preserve the same action/epoch and active authority."""
    if not chain:
        return Decision.REJECT
    for parent, child in zip(chain, chain[1:]):
        result = validate_delegation(parent, child)
        if result != Decision.ALLOW:
            return result
    return Decision.ALLOW


def validate_membership_substitution(original, candidate):
    """Membership may narrow explicitly, but silent widening/threshold change is unsafe."""
    if not candidate.active:
        return Decision.HITL_REQUIRED
    if candidate.threshold != original.threshold:
        return Decision.HITL_REQUIRED
    if not candidate.eligible.issubset(original.eligible):
        return Decision.HITL_REQUIRED
    return Decision.ALLOW


def run():
    action = "release"
    base = Constraint(threshold=2, eligible=frozenset({"alice", "bob", "carol"}))
    authorities = [
        Authority("alice", action, True, 10),
        Authority("bob", action, True, 10),
        Authority("carol", action, True, 10),
    ]
    evidence = Evidence(action, 10, True, "authority-registry")

    assert decide(action, authorities, base, evidence) == Decision.ALLOW

    revoked_bob = [authorities[0], Authority("bob", action, False, 11), authorities[2]]
    assert decide(action, revoked_bob, base, evidence) == Decision.ALLOW

    revoked_bob_carol = [authorities[0], Authority("bob", action, False, 11), Authority("carol", action, False, 11)]
    assert decide(action, revoked_bob_carol, base, evidence) == Decision.REJECT

    stale = Evidence(action, 9, True, "authority-registry")
    assert decide(action, authorities, base, stale) == Decision.REJECT
    assert decide(action, authorities, base, evidence, observed_epoch=11) == Decision.UNKNOWN

    parent = Authority("alice", action, True, 10)
    child = Authority("dave", action, True, 10, delegator="alice")
    assert validate_delegation(parent, child) == Decision.ALLOW

    wrong_action = Authority("dave", "delete", True, 10, delegator="alice")
    assert validate_delegation(parent, wrong_action) == Decision.REJECT

    wrong_parent = Authority("dave", action, True, 10, delegator="mallory")
    assert validate_delegation(parent, wrong_parent) == Decision_REJECT

    stale_child = Authority("dave", action, True, 11, delegator="alice")
    assert validate_delegation(parent, stale_child) == Decision_UNKNOWN

    grandchild = Authority("erin", action, True, 10, delegator="dave")
    assert validate_chain([parent, child, grandchild]) == Decision.ALLOW

    revoked_parent = Authority("alice", action, False, 11)
    assert validate_chain([revoked_parent, child, grandchild]) == Decision_REJECT

    narrowed = Constraint(threshold=2, eligible=frozenset({"alice", "bob"}))
    widened = Constraint(threshold=2, eligible=frozenset({"alice", "bob", "carol", "mallory"}))
    threshold_changed = Constraint(threshold=1, eligible=base.eligible)
    assert validate_membership_substitution(base, narrowed) == Decision.ALLOW
    assert validate_membership_substitution(base, widened) == Decision.HITL_REQUIRED
    assert validate_membership_substitution(base, threshold_changed) == Decision.HITL_REQUIRED

    forged = Evidence(action, 10, True, "delegated-claim-without-authority")
    assert decide(action, [authorities[0]], base, forged) == Decision_REJECT

    malformed = Constraint(threshold=0, eligible=base.eligible)
    assert decide(action, authorities, malformed, evidence) == Decision_HITL_REQUIRED
    assert all(name not in globals() for name in ("ThresholdAuthority", "DelegationPrimitive", "AuthoritySet"))

    print("PASS45_PUBLIC: PASS; cases=14")


Decision_REJECT = Decision.REJECT
Decision_UNKNOWN = Decision.UNKNOWN
Decision_HITL_REQUIRED = Decision.HITL_REQUIRED


if __name__ == "__main__":
    run()
