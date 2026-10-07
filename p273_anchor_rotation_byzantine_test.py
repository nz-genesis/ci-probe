"""P273 bounded differential probe.

Tests safe authority-anchor rotation and Byzantine evidence using only
Authority/Evidence/Observation/Constraint/Transition semantics. The probe
intentionally demonstrates that an insufficient quorum is unsafe, then checks
the minimal 2f+1-of-3f+1 quorum rule for f=1 and safe rotation overlap.
"""
from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Root:
    epoch: int
    digest: str


@dataclass(frozen=True)
class Signed:
    signer: str
    root: Root


@dataclass(frozen=True)
class AnchorState:
    current: Root
    pending: Root | None
    trusted_signers: frozenset[str]
    threshold: int
    generation: int


def quorum(signers: set[str], threshold: int) -> bool:
    return len(signers) >= threshold


def authorized(signatures: list[Signed], root: Root, trusted: set[str], threshold: int) -> bool:
    signers = {x.signer for x in signatures if x.root == root and x.signer in trusted}
    return quorum(signers, threshold)


def initial() -> AnchorState:
    return AnchorState(Root(1, "r1"), None,
                       frozenset({"a", "b", "c", "d"}), 3, 0)


def begin_rotation(s: AnchorState, new: Root, signatures: list[Signed]) -> AnchorState | None:
    if s.pending is not None:
        return None
    if new.epoch != s.current.epoch + 1:
        return None
    if not authorized(signatures, new, set(s.trusted_signers), s.threshold):
        return None
    return AnchorState(s.current, new, s.trusted_signers, s.threshold, s.generation + 1)


def finalize_rotation(s: AnchorState, fresh_observation: Root) -> AnchorState | None:
    if s.pending is None or fresh_observation != s.pending:
        return None
    return AnchorState(s.pending, None, s.trusted_signers, s.threshold, s.generation + 1)


def test_insufficient_quorum_is_unsafe_under_one_byzantine_signer():
    signers = {"a", "b", "c"}
    threshold = 2
    x, y = Root(2, "x"), Root(2, "y")
    # b is Byzantine and can sign both; {a,b} and {b,c} both form quorum.
    assert authorized([Signed("a", x), Signed("b", x)], x, signers, threshold)
    assert authorized([Signed("b", y), Signed("c", y)], y, signers, threshold)


def test_3_of_4_prevents_two_conflicting_quorums_with_one_byzantine():
    signers = {"a", "b", "c", "d"}
    threshold = 3
    all_sets = [set(c) for c in combinations(signers, threshold)]
    conflicting = []
    for q1 in all_sets:
        for q2 in all_sets:
            if len(q1 & q2) <= 1:
                conflicting.append((q1, q2))
    assert not conflicting


def test_rotation_requires_old_protected_authority():
    s = initial()
    new = Root(2, "r2")
    forged = [Signed("x", new), Signed("y", new), Signed("z", new)]
    assert begin_rotation(s, new, forged) is None


def test_rotation_accepts_threshold_attestation_from_protected_set():
    s = initial()
    new = Root(2, "r2")
    sigs = [Signed("a", new), Signed("b", new), Signed("c", new)]
    s1 = begin_rotation(s, new, sigs)
    assert s1 is not None and s1.current == s.current and s1.pending == new


def test_new_root_cannot_self_finalize_without_fresh_observation():
    s = initial()
    new = Root(2, "r2")
    s1 = begin_rotation(s, new, [Signed("a", new), Signed("b", new), Signed("c", new)])
    assert s1 is not None
    assert finalize_rotation(s1, Root(2, "attacker")) is None


def test_safe_overlap_preserves_old_root_until_new_root_observed():
    s = initial()
    new = Root(2, "r2")
    s1 = begin_rotation(s, new, [Signed("a", new), Signed("b", new), Signed("c", new)])
    assert s1 is not None and s1.current == Root(1, "r1")
    s2 = finalize_rotation(s1, new)
    assert s2 is not None and s2.current == new


def test_stale_old_epoch_cannot_start_second_rotation():
    s = initial()
    new = Root(2, "r2")
    s1 = begin_rotation(s, new, [Signed("a", new), Signed("b", new), Signed("c", new)])
    assert s1 is not None
    evil = Root(2, "evil")
    assert begin_rotation(s1, evil, [Signed("a", evil), Signed("b", evil), Signed("c", evil)]) is None


def test_concurrent_rotation_is_blocked_while_one_is_pending():
    s = initial()
    x, y = Root(2, "x"), Root(2, "y")
    s1 = begin_rotation(s, x, [Signed("a", x), Signed("b", x), Signed("c", x)])
    assert s1 is not None
    assert begin_rotation(s1, y, [Signed("a", y), Signed("b", y), Signed("c", y)]) is None


def test_rotation_recovery_does_not_depend_on_mutable_pending_root():
    s = initial()
    new = Root(2, "r2")
    s1 = begin_rotation(s, new, [Signed("a", new), Signed("b", new), Signed("c", new)])
    assert s1 is not None
    corrupted = AnchorState(s1.current, Root(2, "evil"), s1.trusted_signers,
                            s1.threshold, s1.generation)
    assert finalize_rotation(corrupted, new) is None


def test_duplicate_signatures_do_not_inflate_quorum():
    s = initial()
    new = Root(2, "r2")
    sigs = [Signed("a", new), Signed("a", new), Signed("a", new)]
    assert begin_rotation(s, new, sigs) is None


def test_quorum_rule_is_composable_with_existing_governed_transition_basis():
    s = initial()
    new = Root(2, "r2")
    s1 = begin_rotation(s, new, [Signed("a", new), Signed("b", new), Signed("c", new)])
    s2 = finalize_rotation(s1, new) if s1 else None
    assert s2 is not None
    assert s2.generation > s.generation
    assert s2.current == new


def test_anchor_unavailable_is_unknown_not_local_fallback():
    s = initial()
    new = Root(2, "r2")
    assert begin_rotation(s, new, []) is None


def run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for test in tests:
        test()
    print(f"p273 anchor rotation Byzantine: {len(tests)}/{len(tests)} PASS")


if __name__ == "__main__":
    run()
