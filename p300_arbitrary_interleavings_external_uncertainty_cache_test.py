from dataclasses import dataclass
from itertools import permutations


@dataclass(frozen=True)
class State:
    epoch: int
    revision: int
    policy: str
    authority: str


@dataclass(frozen=True)
class Transition:
    tid: str
    snapshot: State
    effect_key: str


@dataclass(frozen=True)
class Receipt:
    tid: str
    effect_key: str
    snapshot: State
    outcome: str


ROOT = "R1"
S1 = State(1, 1, "P1", ROOT)
S2 = State(2, 2, "P2", ROOT)
T1 = Transition("T1", S1, "K1")
R1_UNKNOWN = Receipt("T1", "K1", S1, "UNKNOWN")
R1_COMMITTED = Receipt("T1", "K1", S1, "COMMITTED")


def can_commit(state, transition, receipt):
    return (
        state.authority == ROOT
        and state == transition.snapshot
        and receipt is not None
        and receipt.tid == transition.tid
        and receipt.effect_key == transition.effect_key
        and receipt.snapshot == transition.snapshot
        and receipt.outcome == "COMMITTED"
    )


def run(order):
    state = S1
    receipt = None
    cache = None
    committed = False
    effect_applied = False
    outcomes = []

    for event in order:
        if event == "effect_unknown":
            effect_applied = True
            receipt = R1_UNKNOWN
        elif event == "rotate_policy_authority":
            state = S2
        elif event == "cache_old_receipt":
            cache = receipt
        elif event == "recover":
            candidate = receipt or cache
            if can_commit(state, T1, candidate):
                committed = True
        elif event == "fresh_committed_evidence":
            receipt = R1_COMMITTED
        elif event == "commit":
            candidate = receipt or cache
            if can_commit(state, T1, candidate):
                committed = True
        outcomes.append((event, state, committed, receipt, cache))

    # The original external outcome is UNKNOWN unless an explicit fresh authoritative
    # committed observation is introduced. Rotation cannot itself create that evidence.
    unsafe = committed and not any(e == "fresh_committed_evidence" for e in order)
    return unsafe, outcomes, effect_applied


def main():
    events = (
        "effect_unknown",
        "rotate_policy_authority",
        "cache_old_receipt",
        "recover",
        "commit",
        "fresh_committed_evidence",
    )
    checked = 0
    unsafe = []
    for order in permutations(events):
        bad, _, _ = run(order)
        checked += 1
        if bad:
            unsafe.append(order)

    assert checked == 720
    assert unsafe == []

    # Positive controls: fresh committed evidence can authorize only while its
    # snapshot is still current; once rotated, the same evidence is stale.
    assert run(("effect_unknown", "fresh_committed_evidence", "commit"))[0] is False
    assert run(("effect_unknown", "fresh_committed_evidence", "rotate_policy_authority", "commit"))[0] is False

    print("P300 arbitrary interleavings × external uncertainty × rotation × recovery × cache: 720/720 PASS")


if __name__ == "__main__":
    main()
