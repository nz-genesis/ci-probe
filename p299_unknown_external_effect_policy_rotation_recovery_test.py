from dataclasses import dataclass
from enum import Enum


class Outcome(Enum):
    UNKNOWN = "UNKNOWN"
    COMMITTED = "COMMITTED"
    ABORTED = "ABORTED"


@dataclass(frozen=True)
class State:
    epoch: int
    revision: int
    policy_digest: str
    authority_root: str


@dataclass(frozen=True)
class Transition:
    transition_id: str
    state: State
    effect_key: str


@dataclass(frozen=True)
class Receipt:
    effect_key: str
    transition_id: str
    outcome: Outcome
    state: State


PROTECTED_ROOT = "R1"


def qualifies(current: State, t: Transition, receipt: Receipt | None) -> bool:
    if current.authority_root != PROTECTED_ROOT:
        return False
    if t.state != current:
        return False
    if receipt is None:
        return False
    if receipt.effect_key != t.effect_key or receipt.transition_id != t.transition_id:
        return False
    if receipt.state != t.state:
        return False
    return receipt.outcome is Outcome.COMMITTED


def recover(current: State, t: Transition, receipt: Receipt | None) -> Outcome:
    if receipt is None or receipt.outcome is Outcome.UNKNOWN:
        return Outcome.UNKNOWN
    if not qualifies(current, t, receipt):
        return Outcome.UNKNOWN
    return Outcome.COMMITTED


def main():
    s1 = State(7, 41, "P1", PROTECTED_ROOT)
    s2 = State(8, 42, "P2", PROTECTED_ROOT)
    s3 = State(8, 43, "P2", PROTECTED_ROOT)
    s_bad_root = State(8, 42, "P2", "DERIVED")

    t1 = Transition("T1", s1, "K1")
    r1_unknown = Receipt("K1", "T1", Outcome.UNKNOWN, s1)
    r1_committed = Receipt("K1", "T1", Outcome.COMMITTED, s1)

    # 1. Unknown external result cannot become committed under the same state.
    assert recover(s1, t1, r1_unknown) is Outcome.UNKNOWN

    # 2. A later policy generation cannot upgrade the old unknown result.
    assert recover(s2, t1, r1_unknown) is Outcome.UNKNOWN

    # 3. A later authority generation cannot upgrade it either.
    s2_authority = State(8, 42, "P2", "R2")
    assert recover(s2_authority, t1, r1_unknown) is Outcome.UNKNOWN

    # 4. A later revision cannot upgrade it.
    assert recover(s3, t1, r1_unknown) is Outcome.UNKNOWN

    # 5. A cached old committed receipt cannot be used after state rotation.
    assert recover(s2, t1, r1_committed) is Outcome.UNKNOWN

    # 6. Receipt transition identity cannot be substituted for a new transition.
    t2 = Transition("T2", s2, "K2")
    assert recover(s2, t2, r1_committed) is Outcome.UNKNOWN

    # 7. Receipt effect identity cannot be substituted either.
    r_wrong_effect = Receipt("K2", "T1", Outcome.COMMITTED, s1)
    assert recover(s2, t2, r_wrong_effect) is Outcome.UNKNOWN

    # 8. Policy digest disagreement cannot turn unknown into committed.
    r_policy_old = Receipt("K2", "T2", Outcome.COMMITTED, s1)
    assert recover(s2, t2, r_policy_old) is Outcome.UNKNOWN

    # 9. Unprotected authority root cannot qualify a recovery commit.
    t_bad_root = Transition("T3", s_bad_root, "K3")
    r_bad_root = Receipt("K3", "T3", Outcome.COMMITTED, s_bad_root)
    assert recover(s_bad_root, t_bad_root, r_bad_root) is Outcome.UNKNOWN

    # 10. A fresh, correctly bound committed receipt may recover normally.
    t4 = Transition("T4", s2, "K4")
    r4 = Receipt("K4", "T4", Outcome.COMMITTED, s2)
    assert recover(s2, t4, r4) is Outcome.COMMITTED

    # 11. Reusing T4's receipt after a revision change is rejected.
    assert recover(s3, t4, r4) is Outcome.UNKNOWN

    # 12. Unknown remains unknown even when a new generation presents a fresh verifier view.
    t5 = Transition("T5", s2, "K5")
    r5_unknown = Receipt("K5", "T5", Outcome.UNKNOWN, s2)
    assert recover(s2, t5, r5_unknown) is Outcome.UNKNOWN

    print("P299 unknown external effect × policy/authority rotation × recovery: 12/12 PASS")


if __name__ == "__main__":
    main()
