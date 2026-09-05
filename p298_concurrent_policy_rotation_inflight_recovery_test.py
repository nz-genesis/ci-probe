from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    epoch: int
    revision: int
    policy_digest: str
    authority_root: str


@dataclass(frozen=True)
class Transition:
    epoch: int
    revision: int
    policy_digest: str
    authority_root: str
    operation: str


CURRENT_ROOTS = frozenset({"R1", "R2"})
CHANGE = "change"


def qualify(t: Transition, s: State) -> bool:
    return (
        t.operation == CHANGE
        and t.epoch == s.epoch
        and t.revision == s.revision
        and t.policy_digest == s.policy_digest
        and t.authority_root == s.authority_root
        and s.authority_root in CURRENT_ROOTS
    )


def commit(t: Transition, s: State):
    if not qualify(t, s):
        return False, s
    return True, State(s.epoch, s.revision + 1, s.policy_digest, s.authority_root)


def rotate_policy(s: State, digest: str, root: str):
    return State(s.epoch + 1, s.revision + 1, digest, root)


def main():
    s0 = State(4, 7, "P4", "R1")
    t0 = Transition(4, 7, "P4", "R1", CHANGE)

    # 1. A current transition commits against the exact snapshot.
    ok, s1 = commit(t0, s0)
    assert ok and s1.revision == 8
    # 2. Policy rotation invalidates an in-flight old transition.
    rotated = rotate_policy(s0, "P5", "R2")
    assert not commit(t0, rotated)[0]
    # 3. Authority rotation invalidates an old transition even if policy is unchanged.
    authority_rotated = State(5, 8, "P4", "R2")
    assert not commit(t0, authority_rotated)[0]
    # 4. Revision-only change invalidates the old snapshot.
    revised = State(4, 8, "P4", "R1")
    assert not commit(t0, revised)[0]
    # 5. A transition requalified against the current state can commit.
    t_current = Transition(5, 8, "P5", "R2", CHANGE)
    ok, s2 = commit(t_current, rotated)
    assert ok and s2.revision == 9
    # 6. Recovery cannot resurrect the stale transition after rotation.
    recovered = rotated
    assert not commit(t0, recovered)[0]
    # 7. A forged transition with the current epoch but old policy cannot commit.
    forged = Transition(5, 8, "P4", "R2", CHANGE)
    assert not commit(forged, rotated)[0]
    # 8. A forged transition with current policy but old authority cannot commit.
    forged_root = Transition(5, 8, "P5", "R1", CHANGE)
    assert not commit(forged_root, rotated)[0]
    # 9. A transition with a future revision cannot commit out of order.
    future = Transition(5, 99, "P5", "R2", CHANGE)
    assert not commit(future, rotated)[0]
    # 10. A non-change operation cannot use the protected commit path.
    noop = Transition(5, 8, "P5", "R2", "observe")
    assert not commit(noop, rotated)[0]
    # 11. Two concurrent transitions from the same snapshot: at most one commits.
    ta = Transition(4, 7, "P4", "R1", CHANGE)
    tb = Transition(4, 7, "P4", "R1", CHANGE)
    oka, sa = commit(ta, s0)
    okb, sb = commit(tb, sa)
    assert oka and not okb and sb == sa
    # 12. Recovery followed by a second rotation cannot make the first stale transition current.
    r2 = rotate_policy(sa, "P6", "R2")
    assert not commit(ta, r2)[0]

    print("P298 concurrent policy rotation / in-flight recovery: 12/12 PASS")


if __name__ == "__main__":
    main()
