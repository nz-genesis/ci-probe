"""Bounded external-effect / independent-observation probe for Genesis.

The executor acknowledgement is intentionally separate from the external-world
state and from an observer. The probe tests the semantic distinction between
"execution returned" and "world effect is independently observed".
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class World:
    effects: frozenset[str]


@dataclass(frozen=True)
class Execution:
    operation_id: str
    acknowledged: bool


def execute(world: World, operation_id: str, effect_id: str) -> tuple[World, Execution]:
    if effect_id in world.effects:
        return world, Execution(operation_id, True)
    return World(world.effects | {effect_id}), Execution(operation_id, True)


def observe(world: World, effect_id: str) -> bool:
    # Independent observation reads world state, not executor acknowledgement.
    return effect_id in world.effects


def main() -> None:
    world0 = World(frozenset())

    # Acknowledged execution and independent observation agree on the effect.
    world1, ack1 = execute(world0, "op-1", "effect-1")
    assert ack1.acknowledged
    assert observe(world1, "effect-1")

    # Simulated timeout after external effect: acknowledgement is unavailable,
    # but independent observation still establishes that the world changed.
    timed_out_execution = Execution("op-2", False)
    world2 = World(frozenset({"effect-2"}))
    assert not timed_out_execution.acknowledged
    assert observe(world2, "effect-2")

    # Acknowledgement alone must not be treated as world observation.
    ack_only = Execution("op-3", True)
    world3 = World(frozenset())
    assert ack_only.acknowledged
    assert not observe(world3, "effect-3")

    # Re-execution with the same external effect identity does not create a
    # second observable effect in the bounded idempotent world model.
    world4, _ = execute(world1, "op-1-retry", "effect-1")
    assert world4.effects == world1.effects
    assert observe(world4, "effect-1")

    # Different effect identity remains distinguishable.
    world5, _ = execute(world4, "op-4", "effect-4")
    assert observe(world5, "effect-4")
    assert len(world5.effects) == len(world4.effects) + 1

    print("EXTERNAL EFFECT INDEPENDENT OBSERVATION: 6/6 PASS")
    print("Invariant: execution acknowledgement is not equivalent to independent world observation")


if __name__ == "__main__":
    main()
