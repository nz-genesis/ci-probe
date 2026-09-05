"""P303 bounded adversarial probe.

Three concurrent transitions start under protected generation G1. Each may observe an
external effect as UNKNOWN and later obtain a fresh external observation. Two
independent governance rotations can occur at arbitrary gaps in the merged
order-preserving schedule. Old observations may remain in cache, and commit attempts
are tested against own, cross-transition, and cached evidence.

The key separation is intentional: an external observation is evidence about an
immutable effect identity and may remain factually useful across generations; it does
NOT preserve authorization. A local commit requires a current protected authorization
binding plus matching effect evidence. This prevents recovery from silently turning an
old authorization into a new-generation state transition.

This is a bounded executable model, not a distributed-systems proof.
"""
from itertools import combinations

ROOT = "R0"
TRACE = ("AUTH", "UNKNOWN", "OBSERVE", "COMMIT")


def interleavings_three():
    positions = [0, 0, 0]
    path = []

    def rec():
        if positions == [4, 4, 4]:
            yield tuple(path)
            return
        for tid in range(3):
            if positions[tid] < 4:
                event = TRACE[positions[tid]]
                positions[tid] += 1
                path.append((tid, event))
                yield from rec()
                path.pop()
                positions[tid] -= 1

    yield from rec()


def qualifies(tid, authorization, current, evidence):
    return (
        authorization[tid] == current
        and current["authority"] == ROOT
        and evidence["transition"] == tid
        and evidence["effect"] == f"E{tid + 1}"
        and evidence["observed"]
    )


def main():
    base = {"epoch": 1, "revision": 1, "policy": "P1", "authority": ROOT}
    checked = 0
    unsafe = []

    # Two rotations are inserted into every order-preserving interleaving at distinct
    # gaps 0..12. Each transition has exactly one authorization snapshot at AUTH.
    for path in interleavings_three():
        for r1, r2 in combinations(range(13), 2):
            current = dict(base)
            authorization = [None, None, None]
            observed = [False, False, False]
            cache = {}
            pos = 0
            committed = set()
            for tid, event in path:
                if pos in (r1, r2):
                    current = {
                        "epoch": current["epoch"] + 1,
                        "revision": current["revision"] + 1,
                        "policy": f"P{current['epoch'] + 1}",
                        "authority": f"R{current['epoch']}",
                    }
                if event == "AUTH":
                    authorization[tid] = dict(current)
                elif event == "UNKNOWN":
                    pass
                elif event == "OBSERVE":
                    observed[tid] = True
                    cache[tid] = {
                        "transition": tid,
                        "effect": f"E{tid + 1}",
                        "observed": True,
                    }
                elif event == "COMMIT":
                    candidates = [
                        {"transition": tid, "effect": f"E{tid + 1}", "observed": observed[tid]},
                        {"transition": (tid + 1) % 3, "effect": f"E{((tid + 1) % 3) + 1}", "observed": observed[(tid + 1) % 3]},
                        cache.get(tid, {"transition": tid, "effect": f"E{tid + 1}", "observed": False}),
                    ]
                    outcomes = [qualifies(tid, authorization, current, e) for e in candidates]
                    if outcomes[0]:
                        committed.add(tid)
                    if outcomes[1] or (outcomes[2] and authorization[tid] != current):
                        unsafe.append((path, r1, r2, tid, outcomes, current, authorization[tid]))
                pos += 1
            if len(committed) > 3:
                unsafe.append(("duplicate", path, r1, r2, committed))
            checked += 1

    assert not unsafe, unsafe[:1]
    print(f"P303 exhaustive bounded adversarial cases: {checked}/{checked} PASS")


if __name__ == "__main__":
    main()
