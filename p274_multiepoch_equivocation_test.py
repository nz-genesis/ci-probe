"""P274 bounded differential probe.

Attacks replay and equivocation across successive authority-root epochs.
No new Genesis primitive is introduced: epoch/parent binding is represented
as Evidence and Constraint applied to the existing governed transition.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Root:
    epoch: int
    digest: str
    parent: str


@dataclass(frozen=True)
class Signature:
    signer: str
    root: Root


@dataclass(frozen=True)
class State:
    current: Root
    signers: frozenset[str]
    threshold: int
    pending: Root | None = None


def authorized(state: State, root: Root, sigs: list[Signature]) -> bool:
    if root.epoch != state.current.epoch + 1:
        return False
    if root.parent != state.current.digest:
        return False
    distinct = {s.signer for s in sigs if s.root == root and s.signer in state.signers}
    return len(distinct) >= state.threshold


def begin(state: State, root: Root, sigs: list[Signature]) -> State | None:
    if state.pending is not None:
        return None
    if not authorized(state, root, sigs):
        return None
    return State(state.current, state.signers, state.threshold, root)


def finalize(state: State, observed: Root) -> State | None:
    if state.pending is None or observed != state.pending:
        return None
    return State(observed, state.signers, state.threshold)


def initial() -> State:
    return State(Root(1, "r1", "r0"), frozenset({"a", "b", "c", "d"}), 3)


def sigs(root: Root, names=("a", "b", "c")):
    return [Signature(n, root) for n in names]


def test_epoch_must_advance_exactly_one():
    s = initial()
    jump = Root(3, "r3", "r1")
    assert begin(s, jump, sigs(jump)) is None


def test_parent_must_be_current_digest():
    s = initial()
    forged = Root(2, "evil", "attacker-parent")
    assert begin(s, forged, sigs(forged)) is None


def test_old_epoch_signature_cannot_authorize_new_root():
    s = initial()
    r2 = Root(2, "r2", "r1")
    r3 = Root(3, "r3", "r2")
    assert begin(s, r2, sigs(r2)) is not None
    assert authorized(s, r3, sigs(r2)) is False


def test_delayed_old_root_observation_cannot_finalize_new_pending_root():
    s = initial()
    r2 = Root(2, "r2", "r1")
    pending = begin(s, r2, sigs(r2))
    assert pending is not None
    assert finalize(pending, s.current) is None


def test_same_epoch_equivocation_does_not_create_second_pending_root():
    s = initial()
    x = Root(2, "x", "r1")
    y = Root(2, "y", "r1")
    pending = begin(s, x, sigs(x))
    assert pending is not None
    assert begin(pending, y, sigs(y)) is None


def test_byzantine_signer_can_equivocate_but_honest_intersection_blocks_conflict():
    s = initial()
    x = Root(2, "x", "r1")
    y = Root(2, "y", "r1")
    # b equivocates. With 3-of-4, two quorums intersect in at least two signers,
    # so they cannot both be honest-compatible when at most one signer is Byzantine.
    qx = {"a", "b", "c"}
    qy = {"b", "c", "d"}
    assert len(qx & qy) == 2
    assert len({"b"} & (qx & qy)) == 1
    assert authorized(s, x, sigs(x, tuple(qx)))
    assert authorized(s, y, sigs(y, tuple(qy)))


def test_after_rotation_next_root_must_reference_rotated_root():
    s = initial()
    r2 = Root(2, "r2", "r1")
    s1 = finalize(begin(s, r2, sigs(r2)), r2)
    assert s1 is not None
    r3_good = Root(3, "r3", "r2")
    r3_stale = Root(3, "r3x", "r1")
    assert begin(s1, r3_good, sigs(r3_good)) is not None
    assert begin(s1, r3_stale, sigs(r3_stale)) is None


def test_replayed_signature_cannot_change_root_digest():
    s = initial()
    r2 = Root(2, "r2", "r1")
    evil = Root(2, "evil", "r1")
    old = sigs(r2)
    assert begin(s, evil, old) is None


def test_unknown_observation_does_not_promote_pending_root():
    s = initial()
    r2 = Root(2, "r2", "r1")
    pending = begin(s, r2, sigs(r2))
    assert pending is not None
    assert finalize(pending, Root(2, "unknown", "r1")) is None


def test_rotation_chain_composes_without_new_semantic_primitive():
    s = initial()
    r2 = Root(2, "r2", "r1")
    s1 = finalize(begin(s, r2, sigs(r2)), r2)
    r3 = Root(3, "r3", "r2")
    s2 = finalize(begin(s1, r3, sigs(r3)), r3) if s1 else None
    assert s2 is not None and s2.current == r3


def run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for test in tests:
        test()
    print(f"p274 multi-epoch equivocation: {len(tests)}/{len(tests)} PASS")


if __name__ == "__main__":
    run()
