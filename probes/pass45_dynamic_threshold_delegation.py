"""Pass 45: dynamic k-of-n authority and delegation reduction.

Bounded experiment: threshold requirements, membership changes, revocation and
delegation are represented with existing Authority + Transition + Constraint
+ Evidence. Delegation is itself an authorized transition; no Delegation,
ThresholdAuthority, AuthoritySet or other new Genesis primitive is introduced.
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


@dataclass(frozen=True)
class Transition:
    action: str
    target: str


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
    return Decision.ALLOW if len(eligible_active) >= constraint.threshold else Decision.REJECT


def authorize_transition(transition, authority, constraint, evidence):
    """A delegation/grant is an ordinary Transition and cannot exceed authority scope."""
    if not authority.active or authority.epoch != evidence.epoch:
        return Decision.REJECT
    if transition.action != authority.action:
        return Decision.REJECT
    if not constraint.active or transition.target not in constraint.eligible:
        return Decision.HITL_REQUIRED
    if not evidence.valid or evidence.claim != transition.action:
        return Decision.REJECT
    return Decision.ALLOW


def validate_membership_substitution(original, candidate):
    """Silent membership/threshold widening is not admissible."""
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

    # 1: 2-of-3 active authorities allow.
    assert decide(action, authorities, base, evidence) == Decision.ALLOW

    # 2: revoking one member still leaves threshold satisfied.
    revoked_bob = [authorities[0], Authority("bob", action, False, 11), authorities[2]]
    assert decide(action, revoked_bob, base, evidence) == Decision.ALLOW

    # 3: revoking two members breaks threshold.
    revoked_bob_carol = [authorities[0], Authority("bob", action, False, 11), Authority("carol", action, False, 11)]
    assert decide(action, revoked_bob_carol, base, evidence) == Decision.REJECT

    # 4: stale evidence cannot authorize the current epoch.
    stale = Evidence(action, 9, True, "authority-registry")
    assert decide(action, authorities, base, stale) == Decision.REJECT

    # 5: newer observed epoch is UNKNOWN, not retry permission.
    assert decide(action, authorities, base, evidence, observed_epoch=11) == Decision.UNKNOWN

    # Delegation is modeled as an ordinary transition: grant-release-to-dave.
    delegate_action = "delegate-release"
    delegate_authority = Authority("alice", delegate_action, True, 10)
    delegate_transition = Transition(delegate_action, "dave")
    delegate_constraint = Constraint(threshold=1, eligible=frozenset({"dave"}))
    delegate_evidence = Evidence(delegate_action, 10, True, "authority-state")

    # 6: explicit authority for the delegation transition permits it.
    assert authorize_transition(delegate_transition, delegate_authority, delegate_constraint, delegate_evidence) == Decision.ALLOW

    # 7: release authority cannot silently substitute for delegation authority.
    release_authority = Authority("alice", action, True, 10)
    assert authorize_transition(delegate_transition, release_authority, delegate_constraint, delegate_evidence) == Decision.REJECT

    # 8: delegation cannot widen target constraint without an explicit change.
    widened_target = Constraint(threshold=1, eligible=frozenset({"dave", "mallory"}))
    assert authorize_transition(delegate_transition, delegate_authority, widened_target, delegate_evidence) == Decision_ALLOW
    assert validate_membership_substitution(delegate_constraint, widened_target) == Decision_HITL_REQUIRED

    # 9: stale delegation evidence is rejected rather than silently current.
    stale_delegate_evidence = Evidence(delegate_action, 9, True, "authority-state")
    assert authorize_transition(delegate_transition, delegate_authority, delegate_constraint, stale_delegate_evidence) == Decision_REJECT

    # 10: revoked delegator cannot create a new delegated authority.
    revoked_delegate_authority = Authority("alice", delegate_action, False, 11)
    assert authorize_transition(delegate_transition, revoked_delegate_authority, delegate_constraint, delegate_evidence) == Decision_REJECT

    # 11: threshold can be satisfied by any k eligible active authorities.
    alternate = [
        Authority("alice", action, True, 10),
        Authority("carol", action, True, 10),
    ]
    assert decide(action, alternate, base, evidence) == Decision_ALLOW

    # 12: forged delegation evidence cannot replace delegation authority.
    forged = Evidence(delegate_action, 10, True, "untrusted-delegated-claim")
    assert authorize_transition(delegate_transition, release_authority, delegate_constraint, forged) == Decision_REJECT

    # 13: malformed threshold fails closed.
    malformed = Constraint(threshold=0, eligible=base.eligible)
    assert decide(action, authorities, malformed, evidence) == Decision_HITL_REQUIRED

    # 14: an explicit narrowing is representable; widening is the unsafe substitution.
    narrowed = Constraint(threshold=2, eligible=frozenset({"alice", "bob"}))
    assert validate_membership_substitution(base, narrowed) == Decision_ALLOW
    assert validate_membership_substitution(base, widened_target) == Decision_HITL_REQUIRED

    # Removal test: no special delegation/threshold ontology exists in the probe.
    assert all(name not in globals() for name in ("DelegationPrimitive", "ThresholdAuthority", "AuthoritySet"))
    print("PASS45_PUBLIC: PASS; cases=14")


Decision_ALLOW = Decision.ALLOW
Decision_REJECT = Decision.REJECT
Decision_UNKNOWN = Decision.UNKNOWN
Decision_HITL_REQUIRED = Decision.HITL_REQUIRED


if __name__ == "__main__":
    run()
