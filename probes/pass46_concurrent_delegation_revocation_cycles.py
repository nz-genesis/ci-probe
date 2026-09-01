"""Pass 46: concurrent delegation/revocation and cyclic-delegation reduction.

Bounded experiment: delegation remains an ordinary Transition; concurrent
state changes are represented by State/Observation/Evidence/Constraint and
must fail closed when the observed state cannot be established consistently.
No DelegationGraph, DelegationPolicy, RevocationManager or new Genesis
primitive is introduced.
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
    source: str
    target: str


@dataclass(frozen=True)
class Constraint:
    allowed_targets: frozenset[str]
    max_depth: int
    active: bool = True


@dataclass(frozen=True)
class Evidence:
    claim: str
    epoch: int
    valid: bool
    source: str


def authorize(transition, authority, constraint, evidence):
    if not constraint.active or not evidence.valid:
        return Decision.HITL_REQUIRED
    if authority.epoch != evidence.epoch:
        return Decision.UNKNOWN
    if not authority.active:
        return Decision.REJECT
    if authority.action != transition.action or authority.subject != transition.source:
        return Decision.REJECT
    if evidence.claim != transition.action:
        return Decision.REJECT
    if transition.target not in constraint.allowed_targets:
        return Decision.HITL_REQUIRED
    return Decision.ALLOW


def concurrent_state_decision(observations):
    """Reconcile observations of one protected authority state fail-closed."""
    if not observations:
        return Decision.UNKNOWN
    epochs = {item.epoch for item in observations}
    states = {item.active for item in observations}
    if len(epochs) != 1:
        return Decision.UNKNOWN
    if len(states) != 1:
        return Decision.CONFLICT
    return Decision.ALLOW if True in states else Decision.REJECT


def validate_chain(chain, constraint):
    """Cycles or depth violations are rejected without a graph primitive."""
    if not chain:
        return Decision.UNKNOWN
    if len(chain) > constraint.max_depth:
        return Decision.HITL_REQUIRED
    nodes = []
    for transition in chain:
        if transition.target not in constraint.allowed_targets:
            return Decision.HITL_REQUIRED
        nodes.extend((transition.source, transition.target))
    if len(nodes) != len(set(nodes)):
        return Decision.REJECT
    return Decision.ALLOW


def run():
    grant = "delegate-release"
    constraint = Constraint(
        allowed_targets=frozenset({"bob", "carol", "dave"}), max_depth=2
    )
    current = Evidence(grant, 20, True, "authority-state")
    alice = Authority("alice", grant, True, 20)
    bob = Authority("bob", grant, True, 20)

    # 1: a valid delegation transition is allowed.
    t1 = Transition(grant, "alice", "bob")
    assert authorize(t1, alice, constraint, current) == Decision.ALLOW

    # 2: revocation observed at the same epoch rejects the delegation.
    revoked = Authority("alice", grant, False, 20)
    assert authorize(t1, revoked, constraint, current) == Decision.REJECT

    # 3: a revocation that races with an older observation cannot become ALLOW.
    old = Evidence(grant, 19, True, "authority-state")
    assert authorize(t1, revoked, constraint, old) == Decision.UNKNOWN

    # 4: conflicting same-epoch observations are explicit CONFLICT.
    assert concurrent_state_decision([
        Authority("alice", grant, True, 20),
        Authority("alice", grant, False, 20),
    ]) == Decision.CONFLICT

    # 5: observations from different epochs remain UNKNOWN.
    assert concurrent_state_decision([
        Authority("alice", grant, True, 20),
        Authority("alice", grant, False, 21),
    ]) == Decision.UNKNOWN

    # 6: a child delegation cannot execute after its parent authority is revoked.
    child = Transition(grant, "bob", "carol")
    revoked_bob = Authority("bob", grant, False, 20)
    assert authorize(child, revoked_bob, constraint, current) == Decision.REJECT

    # 7: cyclic delegation is rejected using the existing transition sequence.
    cycle = [
        Transition(grant, "alice", "bob"),
        Transition(grant, "bob", "alice"),
    ]
    assert validate_chain(cycle, constraint) == Decision.REJECT

    # 8: deeper but acyclic chains are bounded by Constraint.
    deep = [
        Transition(grant, "alice", "bob"),
        Transition(grant, "bob", "carol"),
        Transition(grant, "carol", "dave"),
    ]
    assert validate_chain(deep, constraint) == Decision.HITL_REQUIRED

    # 9: target outside the parent constraint cannot be widened silently.
    widened = Transition(grant, "alice", "mallory")
    assert authorize(widened, alice, constraint, current) == Decision.HITL_REQUIRED

    # 10: a child constraint cannot bypass a revoked parent.
    child_constraint = Constraint(
        allowed_targets=frozenset({"carol"}), max_depth=1
    )
    assert authorize(child, revoked_bob, child_constraint, current) == Decision.REJECT

    # 11: malformed depth fails closed.
    malformed = Constraint(allowed_targets=constraint.allowed_targets, max_depth=0)
    assert validate_chain([t1], malformed) == Decision.HITL_REQUIRED

    # 12: forged evidence cannot authorize a different transition.
    forged = Evidence("release", 20, True, "untrusted")
    assert authorize(t1, alice, constraint, forged) == Decision.REJECT

    # 13: no special delegation graph/policy/revocation primitive exists.
    assert all(
        name not in globals()
        for name in ("DelegationGraph", "DelegationPolicy", "RevocationManager")
    )

    print("PASS46_PUBLIC: PASS; cases=13")


if __name__ == "__main__":
    run()
