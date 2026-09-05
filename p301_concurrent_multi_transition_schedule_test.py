from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class State:
    epoch: int
    revision: int
    policy: str
    authority: str


@dataclass(frozen=True)
class Transition:
    transition_id: str
    snapshot: State
    effect_key: str


@dataclass(frozen=True)
class Receipt:
    transition_id: str
    effect_key: str
    snapshot: State
    outcome: str


ROOT = "R1"
S1 = State(1, 1, "P1", ROOT)
S2 = State(2, 2, "P2", ROOT)

T1 = Transition("T1", S1, "K1")
T2 = Transition("T2", S1, "K2")

UNKNOWN = {
    "T1": Receipt("T1", "K1", S1, "UNKNOWN"),
    "T2": Receipt("T2", "K2", S1, "UNKNOWN"),
}
COMMITTED = {
    "T1": Receipt("T1", "K1", S1, "COMMITTED"),
    "T2": Receipt("T2", "K2", S1, "COMMITTED"),
}
TRANSITIONS = {"T1": T1, "T2": T2}


def can_commit(current: State, transition: Transition, receipt: Receipt | None) -> bool:
    return (
        current.authority == ROOT
        and current == transition.snapshot
        and receipt is not None
        and receipt.transition_id == transition.transition_id
        and receipt.effect_key == transition.effect_key
        and receipt.snapshot == transition.snapshot
        and receipt.outcome == "COMMITTED"
    )


def interleavings(first, second):
    """All order-preserving shuffles of two four-event transition traces."""
    for positions in combinations(range(8), 4):
        selected = set(positions)
        i = j = 0
        out = []
        for pos in range(8):
            if pos in selected:
                out.append(first[i])
                i += 1
            else:
                out.append(second[j])
                j += 1
        yield out


def run(order):
    current = S1
    receipts = {}
    cache = {}
    commit_positions = []

    for position, event in enumerate(order):
        if event == "rotate":
            current = S2
        elif event.startswith("unknown-"):
            tid = event[-2:]
            receipts[tid] = UNKNOWN[tid]
        elif event.startswith("fresh-"):
            tid = event[-2:]
            receipts[tid] = COMMITTED[tid]
        elif event.startswith("cache-"):
            tid = event[-2:]
            cache[tid] = receipts.get(tid)
        elif event.startswith("commit-"):
            tid = event[-2:]
            candidate = receipts.get(tid) or cache.get(tid)
            if can_commit(current, TRANSITIONS[tid], candidate):
                commit_positions.append((tid, position))

    return commit_positions, order.index("rotate")


def main():
    trace1 = ["unknown-T1", "fresh-T1", "cache-T1", "commit-T1"]
    trace2 = ["unknown-T2", "fresh-T2", "cache-T2", "commit-T2"]

    checked = 0
    unsafe = []
    for base in interleavings(trace1, trace2):
        for rotation_position in range(9):
            order = base[:rotation_position] + ["rotate"] + base[rotation_position:]
            commits, rotate_at = run(order)
            checked += 1
            # A transition may commit only before the governance/state rotation.
            # A commit after rotation would mean stale evidence crossed generations.
            if any(position > rotate_at for _, position in commits):
                unsafe.append(order)

    assert checked == 630
    assert unsafe == []

    # Positive controls: both independent transitions can commit concurrently
    # before rotation, but neither can commit after rotation.
    commits, rotate_at = run((
        "unknown-T1", "fresh-T1", "cache-T1", "commit-T1",
        "unknown-T2", "fresh-T2", "cache-T2", "commit-T2",
        "rotate",
    ))
    assert {tid for tid, _ in commits} == {"T1", "T2"}
    assert all(position < rotate_at for _, position in commits)

    commits, rotate_at = run((
        "unknown-T1", "fresh-T1", "cache-T1", "commit-T1",
        "unknown-T2", "fresh-T2", "cache-T2", "rotate",
        "commit-T2",
    ))
    assert {tid for tid, _ in commits} == {"T1"}
    assert all(position < rotate_at for _, position in commits)

    print("P301 concurrent two-transition bounded schedule: 630/630 PASS")


if __name__ == "__main__":
    main()
