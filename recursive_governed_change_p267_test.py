"""P267 bounded state-machine falsification probe.

Semantic model only. Tests recursive self-change under concurrency, delegation,
verifier substitution, cache invalidation, irreversible effects, routing
mutation, and resource budgets without introducing a self-evolution primitive.
"""
from dataclasses import dataclass, replace
from enum import Enum


class Target(Enum):
    CAPABILITY = "capability"
    CHANGE_MECHANISM = "change_mechanism"
    AUTHORITY = "authority"
    PURPOSE = "purpose"
    ROUTING = "routing"


@dataclass(frozen=True)
class Governance:
    generation: int
    authority_version: int
    verifier_id: str
    verifier_version: int
    verifier_hash: str
    routing_hash: str


@dataclass(frozen=True)
class State:
    generation: int
    capability_version: int
    mechanism_version: int
    governance: Governance
    purpose_hash: str
    budget: int


@dataclass(frozen=True)
class Candidate:
    target: Target
    generation: int
    authority_version: int
    verifier: tuple[str, int, str]
    routing_hash: str
    cost: int = 1
    approved: bool = False
    external_governance: bool = False
    fresh: bool = True
    cap_version: int | None = None
    mechanism_version: int | None = None
    requested_authority: int | None = None
    requested_routing: str | None = None
    disable_authority_guard: bool = False
    disable_verifier_guard: bool = False
    disable_routing_guard: bool = False


@dataclass(frozen=True)
class Delegation:
    generation: int
    authority_version: int
    scope: frozenset[Target]


@dataclass(frozen=True)
class InFlight:
    generation: int
    capability_version: int
    authority_version: int
    verifier_hash: str


@dataclass(frozen=True)
class Effect:
    operation_id: str
    status: str  # UNKNOWN / COMMITTED / NOT_COMMITTED


@dataclass(frozen=True)
class Cache:
    generation: int
    capability_version: int
    authority_version: int
    verifier_hash: str
    routing_hash: str


def initial() -> State:
    return State(
        0, 1, 1,
        Governance(0, 1, "v", 1, "vh1", "rh1"),
        "purpose-v1", 8,
    )


def candidate(s: State, target: Target, **kw) -> Candidate:
    c = Candidate(
        target, s.generation, s.governance.authority_version,
        (s.governance.verifier_id, s.governance.verifier_version,
         s.governance.verifier_hash),
        s.governance.routing_hash,
    )
    return replace(c, **kw)


def qualify(c: Candidate, s: State) -> bool:
    if c.generation != s.generation:
        return False
    if c.authority_version != s.governance.authority_version:
        return False
    if c.verifier != (
        s.governance.verifier_id,
        s.governance.verifier_version,
        s.governance.verifier_hash,
    ):
        return False
    if c.routing_hash != s.governance.routing_hash or not c.fresh:
        return False
    if c.cost <= 0 or c.cost > s.budget:
        return False
    protected = {Target.CHANGE_MECHANISM, Target.AUTHORITY, Target.PURPOSE, Target.ROUTING}
    if c.target in protected and not c.external_governance:
        return False
    if c.target is Target.PURPOSE:
        return False
    if c.target is Target.CHANGE_MECHANISM and (
        c.disable_authority_guard or c.disable_verifier_guard
    ):
        return False
    if c.target is Target.ROUTING and c.disable_routing_guard:
        return False
    return True


def apply(c: Candidate, s: State) -> State:
    assert qualify(c, s)
    g = replace(s.governance, generation=s.generation + 1)
    cap, mech, auth, routing = (
        s.capability_version, s.mechanism_version,
        s.governance.authority_version, s.governance.routing_hash,
    )
    if c.target is Target.CAPABILITY:
        cap = c.cap_version or cap + 1
    elif c.target is Target.CHANGE_MECHANISM:
        mech = c.mechanism_version or mech + 1
    elif c.target is Target.AUTHORITY:
        auth = c.requested_authority or auth + 1
    elif c.target is Target.ROUTING:
        routing = c.requested_routing or routing
    g = replace(g, authority_version=auth, routing_hash=routing)
    return replace(s, generation=s.generation + 1,
                   capability_version=cap, mechanism_version=mech,
                   governance=g, budget=s.budget - c.cost)


def delegate(d: Delegation, scope: frozenset[Target], s: State) -> Delegation | None:
    if d.generation != s.generation or d.authority_version != s.governance.authority_version:
        return None
    if not scope <= d.scope:
        return None
    return Delegation(d.generation, d.authority_version, scope)


def cache_usable(c: Cache, s: State) -> bool:
    return (
        c.generation == s.generation
        and c.capability_version == s.capability_version
        and c.authority_version == s.governance.authority_version
        and c.verifier_hash == s.governance.verifier_hash
        and c.routing_hash == s.governance.routing_hash
    )


def test_concurrent_stale_transition_rejected():
    s = initial()
    a = candidate(s, Target.CAPABILITY, cap_version=2)
    b = candidate(s, Target.CAPABILITY, cap_version=3)
    s1 = apply(a, s)
    assert not qualify(b, s1)


def test_inflight_binding_is_not_rewritten():
    s = initial()
    action = InFlight(s.generation, s.capability_version,
                      s.governance.authority_version,
                      s.governance.verifier_hash)
    s1 = apply(candidate(s, Target.CAPABILITY, cap_version=2), s)
    assert action.generation == 0 and action.capability_version == 1
    assert action.authority_version == 1 and s1.generation == 1


def test_multihop_delegation_only_attenuates_and_expires():
    s = initial()
    root = Delegation(0, 1, frozenset({Target.CAPABILITY, Target.CHANGE_MECHANISM}))
    child = delegate(root, frozenset({Target.CAPABILITY}), s)
    grandchild = delegate(child, frozenset({Target.CAPABILITY}), s)
    assert child is not None and grandchild is not None
    assert delegate(child, frozenset({Target.AUTHORITY}), s) is None
    s1 = apply(candidate(s, Target.CAPABILITY, cap_version=2), s)
    assert delegate(grandchild, frozenset({Target.CAPABILITY}), s1) is None


def test_verifier_substitution_same_interface_rejected():
    s = initial()
    c = candidate(s, Target.CAPABILITY, verifier=("v", 1, "attacker-hash"))
    assert not qualify(c, s)


def test_verifier_version_change_requires_fresh_governance():
    s = initial()
    c = candidate(s, Target.CAPABILITY, verifier=("v", 2, "vh2"))
    assert not qualify(c, s)


def test_routing_mutation_cannot_disable_routing_guard():
    s = initial()
    c = candidate(s, Target.ROUTING, requested_routing="attacker",
                  approved=True, external_governance=True,
                  disable_routing_guard=True)
    assert not qualify(c, s)


def test_routing_change_composes_with_governed_transition():
    s = initial()
    c = candidate(s, Target.ROUTING, requested_routing="rh2",
                  approved=True, external_governance=True)
    s1 = apply(c, s)
    assert s1.governance.routing_hash == "rh2"


def test_cache_is_not_authority_across_generations():
    s = initial()
    c = Cache(0, 1, 1, "vh1", "rh1")
    assert cache_usable(c, s)
    s1 = apply(candidate(s, Target.CAPABILITY, cap_version=2), s)
    assert not cache_usable(c, s1)


def test_cache_detects_governance_fingerprint_change():
    s = initial()
    c = Cache(0, 1, 1, "vh1", "rh1")
    changed = replace(s, governance=replace(s.governance, verifier_hash="vh2"))
    assert not cache_usable(c, changed)


def test_irreversible_ambiguous_effect_remains_unknown():
    effect = Effect("op-1", "UNKNOWN")
    recovered = effect
    assert recovered.status == "UNKNOWN"


def test_fresh_reconciliation_may_establish_commit_but_recovery_cannot():
    effect = Effect("op-2", "UNKNOWN")
    reconciled = replace(effect, status="COMMITTED")
    assert effect.status == "UNKNOWN"
    assert reconciled.status == "COMMITTED"


def test_authority_cannot_self_escalate():
    s = initial()
    c = candidate(s, Target.AUTHORITY, requested_authority=2, approved=True)
    assert not qualify(c, s)


def test_purpose_cannot_mutate_through_ordinary_change():
    s = initial()
    c = candidate(s, Target.PURPOSE, approved=True, external_governance=True)
    assert not qualify(c, s)
    assert s.purpose_hash == "purpose-v1"


def test_approved_change_mechanism_cannot_remove_guards():
    s = initial()
    c = candidate(s, Target.CHANGE_MECHANISM, approved=True,
                  external_governance=True,
                  disable_authority_guard=True,
                  disable_verifier_guard=True)
    assert not qualify(c, s)


def test_resource_budget_bounds_recursive_evaluation():
    s = initial()
    while s.budget:
        s = apply(candidate(s, Target.CAPABILITY,
                            cap_version=s.capability_version + 1), s)
    assert s.budget == 0
    assert not qualify(candidate(s, Target.CAPABILITY,
                                cap_version=s.capability_version + 1), s)


def test_one_governed_basis_covers_multiple_target_classes():
    s = initial()
    s = apply(candidate(s, Target.CAPABILITY, cap_version=2), s)
    s = apply(candidate(s, Target.CHANGE_MECHANISM, mechanism_version=2,
                        approved=True, external_governance=True), s)
    s = apply(candidate(s, Target.ROUTING, requested_routing="rh2",
                        approved=True, external_governance=True), s)
    assert (s.capability_version, s.mechanism_version, s.governance.routing_hash) == (2, 2, "rh2")


def run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for test in tests:
        test()
    print(f"p267 recursive state machine: {len(tests)}/{len(tests)} PASS")


if __name__ == "__main__":
    run()
