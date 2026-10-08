from dataclasses import dataclass
from itertools import product

@dataclass(frozen=True)
class RootState:
    generation: int
    active: frozenset[str]
    authorized: frozenset[str]
    status: str = "AVAILABLE"

@dataclass(frozen=True)
class Proposal:
    proposer: str
    expected_generation: int
    expected_active: frozenset[str]
    replacement: str

def admissible(state: RootState, proposal: Proposal) -> bool:
    return (state.status == "AVAILABLE" and proposal.proposer in state.authorized
            and proposal.proposer in state.active
            and proposal.expected_generation == state.generation
            and proposal.expected_active == state.active
            and proposal.replacement not in state.active)

def commit(state: RootState, proposal: Proposal) -> tuple[RootState, str]:
    if not admissible(state, proposal):
        return state, "REJECT"
    return RootState(state.generation + 1, frozenset({proposal.replacement}),
                     frozenset({proposal.replacement}), "AVAILABLE"), "ACCEPT"

def resolve_conflict(state: RootState, chosen: str) -> tuple[RootState, str]:
    if state.status != "CONFLICT" or chosen not in state.active:
        return state, "REJECT"
    return RootState(state.generation + 1, frozenset({chosen}),
                     frozenset({chosen}), "AVAILABLE"), "RESOLVED"

def make_conflict(state: RootState) -> RootState:
    return RootState(state.generation, frozenset({"B", "C"}),
                     frozenset({"B", "C"}), "CONFLICT")

def make_unavailable(state: RootState) -> RootState:
    return RootState(state.generation, state.active, state.authorized, "UNAVAILABLE")

def initial_proposals() -> tuple[Proposal, Proposal]:
    return (Proposal("A", 1, frozenset({"A"}), "B"),
            Proposal("A", 1, frozenset({"A"}), "C"))

def targeted_checks() -> None:
    pB, pC = initial_proposals()
    s = RootState(1, frozenset({"A"}), frozenset({"A"}))
    s, first = commit(s, pB); s, second = commit(s, pC)
    assert first == "ACCEPT" and second == "REJECT" and s.active == frozenset({"B"})
    s = RootState(1, frozenset({"A"}), frozenset({"A"}))
    s, first = commit(s, pC); s, second = commit(s, pB)
    assert first == "ACCEPT" and second == "REJECT" and s.active == frozenset({"C"})
    s = RootState(1, frozenset({"A"}), frozenset({"A"}))
    s, _ = commit(s, pB); _, stale = commit(s, pC); assert stale == "REJECT"
    conflict = make_conflict(RootState(2, frozenset({"B"}), frozenset({"B"})))
    resolved, result = resolve_conflict(conflict, "B")
    assert result == "RESOLVED" and resolved.generation == 3
    unavailable = make_unavailable(RootState(2, frozenset({"B","C"}), frozenset({"B","C"})))
    _, result = resolve_conflict(unavailable, "B"); assert result == "REJECT"
    conflict = make_conflict(RootState(4, frozenset({"B"}), frozenset({"B"})))
    assert resolve_conflict(conflict, "A")[1] == "REJECT"

def exhaustive_sequences() -> None:
    actions = ("B", "C", "F", "R", "D")
    failures = []
    pB, pC = initial_proposals()
    for length in range(1, 7):
        for seq in product(actions, repeat=length):
            s = RootState(1, frozenset({"A"}), frozenset({"A"}))
            for action in seq:
                if action == "B":
                    prior_generation = s.generation
                    s, r = commit(s, pB)
                    if prior_generation > 1 and r == "ACCEPT": failures.append((seq, "stale-B-accepted"))
                elif action == "C":
                    prior_generation = s.generation
                    s, r = commit(s, pC)
                    if prior_generation > 1 and r == "ACCEPT": failures.append((seq, "stale-C-accepted"))
                elif action == "F": s = make_conflict(s)
                elif action == "R": s, _ = resolve_conflict(s, "B")
                else: s = make_unavailable(s)
            if s.generation > length + 1: failures.append((seq, "generation-overrun"))
    assert not failures, failures[:20]

def mutation_red_team() -> None:
    pB, pC = initial_proposals()
    s = RootState(1, frozenset({"A"}), frozenset({"A"}))
    s, _ = commit(s, pB)
    assert pC.proposer == "A" and commit(s, pC)[1] == "REJECT"
    conflict = make_conflict(RootState(2, frozenset({"B","C"}), frozenset({"B","C"})))
    assert resolve_conflict(conflict, "A")[1] == "REJECT"
    unavailable = make_unavailable(RootState(2, frozenset({"B"}), frozenset({"B"})))
    assert commit(unavailable, Proposal("B",2,unavailable.active,"D"))[1] == "REJECT"

def main() -> None:
    targeted_checks(); exhaustive_sequences(); mutation_red_team()
    print("6/6 targeted multi-root/rotation cases PASS")
    print("19530/19530 exhaustive action sequences PASS")
    print("3/3 mutation Red Team checks PASS")
    print("new Genesis primitive: NOT DEMONSTRATED")
    print("epistemic status: SUPPORTED / BOUNDED / GOVERNANCE-CONFLICT-OPEN")

if __name__ == "__main__": main()
