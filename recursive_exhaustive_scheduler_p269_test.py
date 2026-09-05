"""P269 bounded exhaustive scheduler.

Enumerate all interleavings of two self-changes and two pre-bound external
operations. The probe checks that a stale binding never becomes admissible
again, retries remain idempotent, governance changes invalidate in-flight
bindings, and recursion is resource-bounded.
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

def prepare(op, s):
    return Action(op, s.generation, s.authority, s.verifier)

def self_change(s):
    if s.budget <= 0:
        raise RuntimeError("budget exhausted")
    return replace(s, generation=s.generation + 1, capability=s.capability + 1, budget=s.budget - 1)

def execute(a, s, w):
    if (a.generation, a.authority, a.verifier) != (s.generation, s.authority, s.verifier):
        return False, w
    if a.op in w.committed:
        return True, w
    return True, replace(w, committed=w.committed | {a.op})

def test_all_24_interleavings_reject_stale_bindings():
    s0, w0 = State(), World()
    a0, b0 = prepare("a", s0), prepare("b", s0)
    orders = list(permutations(("change1", "a", "change2", "b")))
    assert len(orders) == 24 and len(set(orders)) == 24
    for order in orders:
        s, w = s0, w0
        for event in order:
            if event.startswith("change"):
                s = self_change(s)
            elif event == "a":
                _, w = execute(a0, s, w)
            else:
                _, w = execute(b0, s, w)
        if order.index("change1") < order.index("a"):
            assert "a" not in w.committed
        if order.index("change1") < order.index("b"):
            assert "b" not in w.committed

def test_retry_after_crash_is_idempotent():
    s, w = State(), World()
    a = prepare("x", s)
    ok1, w1 = execute(a, s, w)
    ok2, w2 = execute(a, s, w1)
    assert ok1 and ok2 and w1 == w2 and w2.committed == frozenset({"x"})

def test_stale_action_cannot_rebind():
    s, w = State(), World()
    a = prepare("y", s)
    s = self_change(s)
    ok, w = execute(a, s, w)
    assert not ok and not w.committed

def test_authority_and_verifier_changes_invalidate_action():
    s, w = State(), World()
    a = prepare("z", s)
    s = replace(s, generation=1, authority=2, verifier="v2")
    ok, w = execute(a, s, w)
    assert not ok and not w.committed

def test_budget_cannot_be_bypassed():
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

def run():
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    for test in tests:
        test()
    print(f"p269 exhaustive bounded scheduler: {len(tests)}/{len(tests)} PASS; schedules=24")

if __name__ == "__main__":
    run()
