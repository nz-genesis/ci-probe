"""Clean-room concurrency/recovery experiment.

Generic executable experiment only. No private Genesis hypotheses, credentials,
private datasets, internal endpoints, or canonical decisions.
"""
from dataclasses import dataclass
from itertools import permutations

@dataclass(frozen=True)
class State:
    accepted: int = 0
    effect: int = 0
    ack: int = 0
    evidence: int = 0
    revoked: bool = False

def apply(state: State, event: str) -> State:
    if event == "revoke":
        return State(state.accepted, state.effect, state.ack, state.evidence, True)
    if event == "deliver" and not state.revoked:
        return State(state.accepted + 1, state.effect, state.ack, state.evidence, state.revoked)
    if event == "effect" and state.accepted:
        return State(state.accepted, state.effect + 1, state.ack, state.evidence, state.revoked)
    if event == "ack" and state.accepted:
        return State(state.accepted, state.effect, state.ack + 1, state.evidence, state.revoked)
    if event == "evidence" and state.effect:
        return State(state.accepted, state.effect, state.ack, state.evidence + 1, state.revoked)
    return state

def classify(state: State) -> str:
    if state.revoked and state.accepted == 0:
        return "REVOKED"
    if state.effect > 1 or state.accepted > 1:
        return "DUPLICATE"
    if state.effect == 1 and state.evidence == 0:
        return "UNKNOWN"
    if state.effect == 1 and state.evidence == 1:
        return "VERIFIED"
    if state.accepted == 1 and state.ack == 0:
        return "UNKNOWN"
    return "PENDING"

def replay_race() -> None:
    outcomes = set()
    for order in permutations(("deliver", "deliver", "effect", "ack")):
        state = State()
        for event in order:
            state = apply(state, event)
        outcomes.add((state, classify(state)))
    assert any(label == "DUPLICATE" for _, label in outcomes)
    assert any(label == "UNKNOWN" for _, label in outcomes)

def unknown_after_effect() -> None:
    state = State()
    for event in ("deliver", "effect", "ack"):
        state = apply(state, event)
    assert classify(state) == "UNKNOWN"
    assert classify(state) != "VERIFIED"
    assert classify(state) != "FAILED"

def late_evidence() -> None:
    state = State()
    for event in ("deliver", "effect"):
        state = apply(state, event)
    assert classify(state) == "UNKNOWN"
    state = apply(state, "evidence")
    assert classify(state) == "VERIFIED"

def revoke_race() -> None:
    before = State()
    for event in ("revoke", "deliver"):
        before = apply(before, event)
    assert before.accepted == 0
    assert classify(before) == "REVOKED"
    during = State()
    for event in ("deliver", "revoke", "effect"):
        during = apply(during, event)
    assert during.accepted == 1
    assert during.effect == 1
    assert classify(during) == "UNKNOWN"

def main() -> None:
    replay_race()
    unknown_after_effect()
    late_evidence()
    revoke_race()
    print("external realization concurrent recovery: PASS")
    print("checks=replay-race,unknown-after-effect,late-evidence,revoke-race")
    print("unknown!=failed; unknown!=verified; duplicate!=ordinary-success")

if __name__ == "__main__":
    main()
