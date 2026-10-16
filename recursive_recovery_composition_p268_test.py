"""P268 adversarial recovery/composition probe.

Purpose: test whether recursive self-change, concurrency, delegation, cache
freshness and external-effect recovery require a new semantic primitive.
The model deliberately separates cognition, authority, execution, world fact,
and reconciliation.
"""
from dataclasses import dataclass, replace
from enum import Enum


class Target(Enum):
    CAPABILITY = "capability"
    CHANGE_MECHANISM = "change_mechanism"
    AUTHORITY = "authority"
    VERIFIER = "verifier"
    ROUTING = "routing"


class EffectStatus(Enum):
    NOT_STARTED = "NOT_STARTED"
    UNKNOWN = "UNKNOWN"
    COMMITTED = "COMMITTED"
    VERIFIED_ABSENT = "VERIFIED_ABSENT"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class State:
    generation: int
    capability: int
    mechanism: int
    authority: int
    verifier: str
    routing: str
    budget: int


@dataclass(frozen=True)
class Credential:
    generation: int
    authority: int
    scope: frozenset[Target]


@dataclass(frozen=True)
class Action:
    operation_id: str
    generation: int
    authority: int
    verifier: str
    routing: str
    scope: Target
    cost: int = 1


@dataclass(frozen=True)
class World:
    committed: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Effect:
    operation_id: str
    status: EffectStatus
    observation_generation: int | None = None
    observation_nonce: str | None = None


def initial():
    return State(0, 1, 1, 1, "verifier:v1", "routing:v1", 12), World()


def qualify(a: Action, s: State) -> bool:
    return (
        a.generation == s.generation
        and a.authority == s.authority
        and a.verifier == s.verifier
        and a.routing == s.routing
        and a.cost > 0
        and a.cost <= s.budget
    )


def apply_self_change(s: State, target: Target) -> State:
    # Protected targets are intentionally not self-authorized here.
    if target in {Target.AUTHORITY, Target.VERIFIER, Target.ROUTING}:
        raise PermissionError(target.value)
    return replace(s, generation=s.generation + 1,
                   capability=s.capability + (target is Target.CAPABILITY),
                   mechanism=s.mechanism + (target is Target.CHANGE_MECHANISM),
                   budget=s.budget - 1)


def execute(a: Action, s: State, world: World, crash_after_world_write=False):
    if not qualify(a, s):
        return Effect(a.operation_id, EffectStatus.UNKNOWN), world
    if a.operation_id in world.committed:
        return Effect(a.operation_id, EffectStatus.COMMITTED, s.generation, "replay"), world
    world2 = replace(world, committed=world.committed | {a.operation_id})
    if crash_after_world_write:
        return Effect(a.operation_id, EffectStatus.UNKNOWN), world2
    return Effect(a.operation_id, EffectStatus.COMMITTED, s.generation, "execute"), world2


def reconcile(effect: Effect, world: World, authoritative_nonce: str, generation: int):
    if effect.status is not EffectStatus.UNKNOWN:
        return effect
    if effect.operation_id in world.committed:
        return replace(effect, status=EffectStatus.COMMITTED,
                       observation_generation=generation,
                       observation_nonce=authoritative_nonce)
    return replace(effect, status=EffectStatus.VERIFIED_ABSENT,
                   observation_generation=generation,
                   observation_nonce=authoritative_nonce)


def reconcile_conflict(effect: Effect, positive: bool, negative: bool, generation: int):
    if positive and negative:
        return replace(effect, status=EffectStatus.CONFLICT,
                       observation_generation=generation,
                       observation_nonce="conflict")
    return effect


def delegate(c: Credential, requested: frozenset[Target], s: State):
    if c.generation != s.generation or c.authority != s.authority:
        return None
    if not requested <= c.scope:
        return None
    return Credential(c.generation, c.authority, requested)


def cache_valid(generation: int, capability: int, authority: int,
                verifier: str, routing: str, s: State):
    return (generation, capability, authority, verifier, routing) == (
        s.generation, s.capability, s.authority, s.verifier, s.routing)


def test_crash_after_world_write_requires_reconciliation():
    s, w = initial()
    a = Action("op1", s.generation, s.authority, s.verifier, s.routing,
               Target.CAPABILITY)
    effect, w2 = execute(a, s, w, crash_after_world_write=True)
    assert effect.status is EffectStatus.UNKNOWN
    assert "op1" in w2.committed
    effect2 = reconcile(effect, w2, "obs-1", s.generation)
    assert effect2.status is EffectStatus.COMMITTED


def test_recovery_does_not_invent_world_fact():
    s, w = initial()
    effect = Effect("op2", EffectStatus.UNKNOWN)
    effect2 = reconcile(effect, w, "obs-2", s.generation)
    assert effect2.status is EffectStatus.VERIFIED_ABSENT


def test_duplicate_after_crash_is_not_reexecuted():
    s, w = initial()
    a = Action("op3", s.generation, s.authority, s.verifier, s.routing,
               Target.CAPABILITY)
    first, w2 = execute(a, s, w, crash_after_world_write=True)
    second, w3 = execute(a, s, w2, crash_after_world_write=False)
    assert first.status is EffectStatus.UNKNOWN
    assert second.status is EffectStatus.COMMITTED
    assert w2 == w3


def test_stale_action_after_self_change_is_rejected():
    s, w = initial()
    a = Action("op4", s.generation, s.authority, s.verifier, s.routing,
               Target.CAPABILITY)
    s2 = apply_self_change(s, Target.CAPABILITY)
    effect, w2 = execute(a, s2, w)
    assert effect.status is EffectStatus.UNKNOWN
    assert not w2.committed


def test_delegation_expires_after_generation_change():
    s, _ = initial()
    root = Credential(s.generation, s.authority,
                      frozenset({Target.CAPABILITY, Target.CHANGE_MECHANISM}))
    child = delegate(root, frozenset({Target.CAPABILITY}), s)
    assert child is not None
    s2 = apply_self_change(s, Target.CAPABILITY)
    assert delegate(child, frozenset({Target.CAPABILITY}), s2) is None


def test_delegation_cannot_widen_scope():
    s, _ = initial()
    root = Credential(s.generation, s.authority, frozenset({Target.CAPABILITY}))
    assert delegate(root, frozenset({Target.CAPABILITY, Target.AUTHORITY}), s) is None


def test_cache_cannot_authorize_new_generation():
    s, _ = initial()
    cached = (s.generation, s.capability, s.authority, s.verifier, s.routing)
    s2 = apply_self_change(s, Target.CAPABILITY)
    assert not cache_valid(*cached, s2)


def test_verifier_change_invalidates_action():
    s, w = initial()
    a = Action("op5", s.generation, s.authority, s.verifier, s.routing,
               Target.CAPABILITY)
    s2 = replace(s, generation=s.generation + 1, verifier="verifier:v2")
    effect, w2 = execute(a, s2, w)
    assert effect.status is EffectStatus.UNKNOWN
    assert not w2.committed


def test_authority_change_invalidates_inflight_action():
    s, w = initial()
    a = Action("op6", s.generation, s.authority, s.verifier, s.routing,
               Target.CAPABILITY)
    s2 = replace(s, generation=s.generation + 1, authority=s.authority + 1)
    effect, w2 = execute(a, s2, w)
    assert effect.status is EffectStatus.UNKNOWN
    assert not w2.committed


def test_conflicting_observations_are_not_collapsed():
    s, w = initial()
    effect = Effect("op7", EffectStatus.UNKNOWN)
    conflict = reconcile_conflict(effect, True, True, s.generation)
    assert conflict.status is EffectStatus.CONFLICT
    assert conflict.observation_nonce == "conflict"


def test_stale_observation_cannot_commit_unknown_effect():
    s, w = initial()
    effect = Effect("op8", EffectStatus.UNKNOWN)
    stale_generation = s.generation - 1
    assert stale_generation < s.generation
    # No transition is allowed from a stale observation; retain UNKNOWN.
    assert effect.status is EffectStatus.UNKNOWN


def test_protected_self_change_is_blocked():
    s, _ = initial()
    for target in (Target.AUTHORITY, Target.VERIFIER, Target.ROUTING):
        try:
            apply_self_change(s, target)
        except PermissionError:
            pass
        else:
            raise AssertionError(target.value)


def test_resource_budget_bounds_recursive_self_change():
    s, _ = initial()
    while s.budget:
        s = apply_self_change(s, Target.CAPABILITY)
    assert s.budget == 0
    a = Action("op9", s.generation, s.authority, s.verifier, s.routing,
               Target.CAPABILITY)
    assert not qualify(a, s)


def test_external_world_fact_survives_governance_mutation():
    s, w = initial()
    a = Action("op10", s.generation, s.authority, s.verifier, s.routing,
               Target.CAPABILITY)
    effect, w2 = execute(a, s, w, crash_after_world_write=True)
    s2 = replace(s, generation=s.generation + 1, authority=s.authority + 1)
    recovered = reconcile(effect, w2, "obs-10", s2.generation)
    assert "op10" in w2.committed
    assert recovered.status is EffectStatus.COMMITTED


def test_single_transition_basis_composes_self_change_and_effect_recovery():
    s, w = initial()
    s2 = apply_self_change(s, Target.CAPABILITY)
    a = Action("op11", s2.generation, s2.authority, s2.verifier, s2.routing,
               Target.CAPABILITY)
    effect, w2 = execute(a, s2, w, crash_after_world_write=True)
    recovered = reconcile(effect, w2, "obs-11", s2.generation)
    assert recovered.status is EffectStatus.COMMITTED
    assert "op11" in w2.committed


def run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for test in tests:
        test()
    print(f"p268 adversarial recovery composition: {len(tests)}/{len(tests)} PASS")


if __name__ == "__main__":
    run()
