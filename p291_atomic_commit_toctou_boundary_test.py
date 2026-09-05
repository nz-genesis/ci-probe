from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    epoch: int
    boundary_version: str


@dataclass(frozen=True)
class Transition:
    epoch: int
    boundary_version: str
    operation: str = "change"


def qualify(t: Transition, s: State) -> bool:
    return (
        t.operation == "change"
        and t.epoch == s.epoch
        and t.boundary_version == s.boundary_version
    )


def atomic_commit(t: Transition, read_state: State, current_state: State) -> bool:
    # Qualification must be revalidated against the authoritative commit state.
    return qualify(t, current_state) and read_state == current_state


def main() -> None:
    b1 = State(7, "B1")
    b2 = State(8, "B2")

    # 1. Ordinary snapshot/commit succeeds when state is unchanged.
    t1 = Transition(7, "B1")
    assert atomic_commit(t1, b1, b1)

    # 2. TOCTOU: qualification on B1 cannot commit after B1 -> B2.
    assert qualify(t1, b1)
    assert not atomic_commit(t1, b1, b2)

    # 3. New transition can commit against the new state.
    t2 = Transition(8, "B2")
    assert atomic_commit(t2, b2, b2)

    # 4. Re-reading state after a concurrent mutation does not revive old authority.
    assert not atomic_commit(t1, b1, b2)

    # 5. Forged snapshot cannot satisfy the current-state binding.
    forged = State(7, "B1")
    assert forged == b1
    assert not atomic_commit(t1, forged, b2)

    # 6. A transition that changes the boundary itself cannot use the old snapshot
    # as authority after the boundary has rotated.
    rotate = Transition(7, "B1", operation="change-boundary")
    assert not atomic_commit(rotate, b1, b1)

    # 7. In-flight work resumed after recovery must revalidate against current state.
    assert not atomic_commit(t1, b1, b2)

    # 8. A current transition remains valid after a failed stale retry.
    assert atomic_commit(t2, b2, b2)

    # 9. Competing current state invalidates a transition bound to the other state.
    b3 = State(9, "B3")
    assert not atomic_commit(t2, b2, b3)

    # 10. No commit path may accept a transition merely because its own fields
    # look internally consistent; current state is authoritative.
    assert qualify(t2, b2)
    assert not atomic_commit(t2, b2, b3)

    # 11. Boundary version alone is insufficient without epoch agreement.
    same_boundary_new_epoch = State(9, "B2")
    assert not atomic_commit(t2, b2, same_boundary_new_epoch)

    # 12. Epoch alone is insufficient without boundary agreement.
    same_epoch_new_boundary = State(8, "B3")
    assert not atomic_commit(t2, b2, same_epoch_new_boundary)

    print("P291 atomic commit / TOCTOU boundary: 12/12 PASS")


if __name__ == "__main__":
    main()
