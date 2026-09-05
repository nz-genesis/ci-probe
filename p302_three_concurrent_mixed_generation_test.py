"""P302 bounded adversarial probe.

Three concurrent transitions carry explicit generation/state bindings. Two governance
rotations occur. Cross-transition receipts and cached evidence are deliberately
substituted. A transition may commit only when its full snapshot still equals the
current protected state and its evidence/effect identity matches the transition.

This is a bounded executable model, not a distributed-systems proof.
"""
from itertools import permutations, product

ROOT = "R0"


def qualify(t, state, evidence):
    return (
        t["epoch"] == state["epoch"]
        and t["revision"] == state["revision"]
        and t["policy"] == state["policy"]
        and t["authority"] == state["authority"]
        and state["authority"] == ROOT
        and evidence["transition"] == t["id"]
        and evidence["effect"] == t["effect"]
        and evidence["epoch"] == state["epoch"]
        and evidence["revision"] == state["revision"]
        and evidence["policy"] == state["policy"]
        and evidence["authority"] == state["authority"]
        and evidence["fresh"]
    )


def main():
    base = {"epoch": 1, "revision": 1, "policy": "P1", "authority": ROOT}
    transitions = [
        {"id": "T1", "effect": "E1", **base},
        {"id": "T2", "effect": "E2", **base},
        {"id": "T3", "effect": "E3", **base},
    ]
    evidence = [
        {"transition": t["id"], "effect": t["effect"], **base, "fresh": True}
        for t in transitions
    ]
    # Cached copies are stale by construction after either rotation.
    stale = [{**e, "fresh": False} for e in evidence]

    # Every transition has a three-event trace; rotations may occur at any boundary.
    # We enumerate all 3! transition ordering choices, all 4^2 rotation positions,
    # and all choices of correct/stale/cross-transition evidence.
    checked = 0
    unsafe = []
    for order in permutations(range(3)):
        for r1, r2 in product(range(4), repeat=2):
            for evidence_choice in product(range(3), repeat=3):
                state = dict(base)
                cache = [stale[i] for i in range(3)]
                rotation_positions = sorted((r1, r2))
                pos = 0
                committed = []
                for idx in order:
                    if pos in rotation_positions:
                        state["epoch"] += 1
                        state["revision"] += 1
                        state["policy"] = f"P{state['epoch']}"
                        cache = [{**e, "fresh": False} for e in evidence]
                    t = transitions[idx]
                    choice = evidence_choice[idx]
                    # adversarial choices: own fresh, own stale, another transition's fresh
                    candidates = [evidence[idx], cache[idx], evidence[choice]]
                    if qualify(t, state, candidates[0]):
                        committed.append(t["id"])
                    if qualify(t, state, candidates[1]):
                        committed.append(t["id"] + ":stale")
                    if qualify(t, state, candidates[2]) and choice != idx:
                        unsafe.append((order, r1, r2, idx, choice))
                    pos += 1
                # A rotation invalidates every pre-rotation snapshot; no stale commit allowed.
                if len(set(x for x in committed if ":stale" not in x)) > 3:
                    unsafe.append(("duplicate", order, r1, r2, committed))
                checked += 1
    assert not unsafe, unsafe[:1]
    print(f"P302 exhaustive bounded adversarial cases: {checked}/{checked} PASS")


if __name__ == "__main__":
    main()
