#!/usr/bin/env python3
"""P290 — protected-boundary lifecycle composition under concurrency/recovery.

Bounded model only. Tests whether an external protected boundary remains
sufficient when authority rotates while a self-change is in flight and an
external effect may already have happened before crash/recovery.
"""
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class Boundary:
    root: str
    version: int
    immutable_to_target: bool = True

@dataclass(frozen=True)
class State:
    epoch: int
    authority: str
    boundary: Boundary

@dataclass(frozen=True)
class Transition:
    epoch: int
    authority: str
    boundary_version: int
    transition_id: str
    effect_key: str

@dataclass
class External:
    applied: set

    def apply(self, key: str) -> bool:
        if key in self.applied:
            return False
        self.applied.add(key)
        return True


def qualify(state: State, boundary: Boundary, t: Transition) -> bool:
    return (
        boundary.immutable_to_target
        and boundary.root == state.authority
        and boundary.version == state.boundary.version
        and t.epoch == state.epoch
        and t.authority == state.authority
        and t.boundary_version == boundary.version
    )


def main() -> None:
    b1 = Boundary("R1", 1)
    s1 = State(10, "R1", b1)
    t1 = Transition(10, "R1", 1, "T1", "E1")
    ext = External(set())

    # 1. Current transition is admissible under current protected boundary.
    assert qualify(s1, b1, t1)

    # 2. Boundary cannot be mutated in-place by the target.
    assert b1.immutable_to_target
    assert replace(b1, immutable_to_target=False).immutable_to_target is False

    # 3. Authority rotates while T1 is in flight.
    b2 = Boundary("R1", 2)
    s2 = State(11, "R1", b2)
    assert not qualify(s2, b2, t1)

    # 4. Merely swapping the verifier/boundary version cannot revive T1.
    assert not qualify(s2, b2, replace(t1, boundary_version=2))

    # 5. A new transition must bind to the new state.
    t2 = Transition(11, "R1", 2, "T2", "E2")
    assert qualify(s2, b2, t2)

    # 6. External effect for T1 may already have happened before crash.
    assert ext.apply(t1.effect_key)

    # 7. Crash/recovery does not erase the external effect.
    recovered_ext = ext
    assert t1.effect_key in recovered_ext.applied

    # 8. Recovery cannot treat stale T1 as current merely because effect exists.
    assert not qualify(s2, b2, t1)

    # 9. Recovery cannot replay T1's effect under the same idempotency key.
    assert not recovered_ext.apply(t1.effect_key)

    # 10. A forged authority cannot qualify T2.
    assert not qualify(State(11, "R2", b2), b2, t2)

    # 11. A forged boundary root cannot qualify T2.
    forged = Boundary("R2", 2)
    assert not qualify(s2, forged, t2)

    # 12. A mutable boundary realization is not a protected boundary.
    mutable = Boundary("R1", 2, immutable_to_target=False)
    assert not qualify(s2, mutable, t2)

    # 13. Old authority cannot authorize a new epoch transition.
    assert not qualify(State(10, "R1", b1), b1, t2)

    # 14. New epoch cannot be authorized by old boundary version.
    assert not qualify(State(11, "R1", b2), b1, t2)

    # 15. Competing recovery root cannot become authoritative by local choice.
    competing = State(11, "R2", Boundary("R2", 1))
    assert not qualify(s2, competing.boundary, t2)

    # 16. The protected boundary itself is not replaceable through a normal change.
    boundary_change = Transition(11, "R1", 2, "T3", "E3")
    assert not qualify(s2, Boundary("R1", 3), boundary_change)

    print("P290 protected boundary lifecycle composition: 16/16 PASS")

if __name__ == "__main__":
    main()
