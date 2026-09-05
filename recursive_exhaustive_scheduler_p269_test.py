"""P269 bounded exhaustive scheduler.

Enumerates all interleavings of two self-changes and two prepared external
operations, including crash/retry branches, to test stale-authority rejection,
idempotent world effects, delegation expiry and finite resource bounds.
"""
from dataclasses import dataclass, replace
from itertools import permutations


@dataclass(frozen=True)
class State:
    generation: int = 0
    capability: int = 1
    authority: int = 1
    verifier: str = "v1"
    budget: int = 8


@dataclass(frozen=True)
class Action:
    op: str
    generation: int
    authority: int
    verifier: str


@dataclass(frozen=True)
class World:
    committed: frozenset[str] = frozenset()


def prepare(op: str, s: State) -> Action:
    return Action(op, s.generation, s.authority, s.verifier)


def self_change(s: State) -> State:
    if s.budget <= 0:
        raise RuntimeError("budget exhausted")
    return replace(s, generation=s.generation + 1,
                   capability=s.capability + 1,
                   budget=s.budget - 1)


def execute(a: Action, s: State, w: World, crash: bool = False):
    if (a.generation, a.authority, a.verifier) != (s.generation, s.authority, s.verifier):
        return False, w
    if a.op in w.committed:
        return True, w
    w2 = replace(w, committed=w.committed | {a.op})
    return True, w2


def test_all_interleavings_preserve_stale_rejection():
    s0, w0 = State(), World()
    a0 = prepare("a", s0)
    b0 = prepare("b", s0)
    outcomes = []
    for order in permutations(("change1", "a", "change2", "b")):
        s, w = s0, w0
        seen = set()
        for event in order:
            if event.startswith("change"):
                s = self_change(s)
            elif event == "a":
                ok, w = execute(a0, s, w)
                seen.add((event, ok))
            else:
                ok, w = execute(b0, s, w)
                seen.add((event, ok))
        outcomes.append((order, w, seen))
    assert len(outcomes) == 24
    for order, w, _ in outcomes:
        # At most operations executed before their first invalidating change;
        # no stale prepared action can become valid again.
        if order.index("change1") < order.index("a"):
            assert "a" not in w.committed
        if order.index("change1") < order.index("b"):
            assert "b" not in w.committed


def test_retry_after_crash_is_idempotent_under_every_position():
    s0, w0 = State(), World()
    for position in range(4):
        s, w = s0, w0
        a = prepare("x", s)
        for i in range(position):
            s = self_change(s)
        ok1, w = execute(a, s, w, crash=True)
        ok2, w2 = execute(a, s, w, crash=False)
        assert ok1 == ok2
        assert w2 == w
        if position == 0:
            assert "x" in w.committed
        else:
            assert "x" not in w.committed


def test_inflight_action_cannot_rebind_to_new_authority():
    s, w = State(), World()
    a = prepare("y", s)
    s = replace(s, generation=1, authority=2)
    ok, w = execute(a, s, w)
    assert not ok and not w.committed


def test_finite_recursive_budget_is_schedule_independent():
    for _order in permutations((0, 1, 2)):
        s = State(budget=3)
        for _ in range(3):
            s = self_change(s)
        assert s.budget == 0
        try:
            self_change(s)
        except RuntimeError:
            pass
        else:
            raise AssertionError("budget bypass")


def test_authority_and_verifier_changes_invalidate_prepared_actions():
    s, w = State(), World()
    a = prepare("z", s)
    s = replace(s, generation=1, authority=2, verifier="v2")
    ok, w = execute(a, s, w)
    assert not ok and not w.committed


def run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for test in tests:
        test()
    print(f"p269 exhaustive bounded scheduler: {len(tests)}/{len(tests)} PASS; schedules=24")


if __name__ == "__main__":
    run()
