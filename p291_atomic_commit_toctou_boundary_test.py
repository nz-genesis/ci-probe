from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    epoch: int
    boundary_version: str
    revision: int


@dataclass(frozen=True)
class Transition:
    epoch: int
    boundary_version: str
    expected_revision: int
    operation: str = "change"


def qualify(t: Transition, s: State) -> bool:
    return (
        t.operation == "change"
        and t.epoch == s.epoch
        and t.boundary_version == s.boundary_version
        and t.expected_revision == s.revision
    )


def atomic_commit(t: Transition, read_state: State, current_state: State) -> bool:
    # The authoritative commit point must atomically revalidate the snapshot.
    return qualify(t, current_state) and read_state == current_state


def main() -> None:
    b1 = State(7, "B1", 41)
    b2 = State(8, "B2", 42)

    # 1. Ordinary snapshot/commit succeeds when the authoritative state is unchanged.
    t1 = Transition(7, "B1", 41)
    assert qualify(t1, b1)
    assert atomic_commit(t1, b1, b1)

    # 2. TOCTOU: T1 qualified on B1 cannot commit after B1 -> B2.
    assert not atomic_commit(t1, b1, b2)

    # 3. A transition explicitly bound to the new state can commit.
    t2 = Transition(8, "B2", 42)
    assert qualify(t2, b2)
    assert atomic_commit(t2, b2, b2)

    # 4. A stale in-flight retry cannot be revived by the old snapshot.
    assert not atomic_commit(t1, b1, b2)

    # 5. A snapshot with matching semantic fields but an obsolete revision is stale.
    stale_same_fields = State(7, "B1", 40)
    assert not qualify(t1, stale_same_fields)
    assert not atomic_commit(t1, stale_same_fields, b1)

    # 6. Boundary-changing operation is not a normal governed change.
    rotate = Transition(7, "B1", 41, operation="change-boundary")
    assert not qualify(rotate, b1)
    assert not atomic_commit(rotate, b1, b1)

    # 7. Resumed in-flight work after recovery must revalidate the current revision.
    assert not atomic_commit(t1, b1, b2)

    # 8. A valid current transition remains valid when no competing mutation occurs.
    assert atomic_commit(t2, b2, b2)

    # 9. A competing successor state invalidates T2.
    b3 = State(9, "B3", 43)
    assert not atomic_commit(t2, b2, b3)

    # 10. Internal consistency of T2 cannot substitute for authoritative state.
    assert qualify(t2, b2)
    assert not atomic_commit(t2, b2, b3)

    # 11. Matching boundary but changed epoch/revision is rejected.
    same_boundary_new_epoch = State(9, "B2", 43)
    assert not atomic_commit(t2, b2, same_boundary_new_epoch)

    # 12. Matching epoch but changed boundary/revision is rejected.
    same_epoch_new_boundary = State(8, "B3", 43)
    assert not atomic_commit(t2, b2, same_epoch_new_boundary)

    print("P291 atomic commit / TOCTOU boundary: 12/12 PASS")


if __name__ == "__main__":
    main()
