from dataclasses import dataclass


@dataclass(frozen=True)
class Authority:
    root: str
    epoch: int


@dataclass(frozen=True)
class Verifier:
    verifier_id: str
    trusted_root: str
    epoch: int
    guard_intact: bool
    dependency: str


@dataclass(frozen=True)
class Transition:
    transition_id: str
    epoch: int
    authority_root: str
    verifier_id: str
    verifier_dependency: str
    expected_revision: int
    operation: str
    target: str


@dataclass
class State:
    epoch: int
    authority_root: str
    verifier_id: str
    verifier_dependency: str
    revision: int


TRUSTED_ROOT = "R0"
PROTECTED_VERIFIER = "V0"
PROTECTED_DEPENDENCY = "D0"


def qualify(state: State, t: Transition, verifiers: dict[str, Verifier], authorities: set[Authority]) -> bool:
    v = verifiers.get(t.verifier_id)
    current_authority = Authority(state.authority_root, state.epoch)
    if current_authority not in authorities:
        return False
    if t.epoch != state.epoch or t.expected_revision != state.revision:
        return False
    if t.authority_root != state.authority_root:
        return False
    if t.operation not in {"change_verifier", "change_dependency", "change_capability"}:
        return False
    if v is None or not v.guard_intact:
        return False
    if v.epoch != state.epoch or v.trusted_root != TRUSTED_ROOT:
        return False
    if t.verifier_dependency != v.dependency:
        return False
    # The candidate verifier/dependency may be the target, but it cannot redefine
    # the protected trust root or the protected qualification boundary used here.
    if t.target == TRUSTED_ROOT or t.target == PROTECTED_VERIFIER or t.target == PROTECTED_DEPENDENCY:
        return False
    return True


def commit(state: State, t: Transition, verifiers: dict[str, Verifier], authorities: set[Authority]) -> bool:
    if not qualify(state, t, verifiers, authorities):
        return False
    state.revision += 1
    return True


def main():
    authorities = {Authority(TRUSTED_ROOT, 1), Authority(TRUSTED_ROOT, 2)}
    verifiers = {
        "V0": Verifier("V0", TRUSTED_ROOT, 1, True, PROTECTED_DEPENDENCY),
        "V1": Verifier("V1", TRUSTED_ROOT, 1, True, "D1"),
        "Vweak": Verifier("Vweak", TRUSTED_ROOT, 1, False, "D1"),
        "Vstale": Verifier("Vstale", TRUSTED_ROOT, 0, True, "D0"),
        "Vevil": Verifier("Vevil", "R-EVIL", 1, True, "D-EVIL"),
        "V2": Verifier("V2", TRUSTED_ROOT, 2, True, "D2"),
    }
    state = State(1, TRUSTED_ROOT, PROTECTED_VERIFIER, PROTECTED_DEPENDENCY, 10)

    # 1. Baseline governed capability change is accepted.
    t1 = Transition("T1", 1, TRUSTED_ROOT, "V0", PROTECTED_DEPENDENCY, 10, "change_capability", "C1")
    assert commit(state, t1, verifiers, authorities)
    assert state.revision == 11

    # 2. A verifier replacement may be accepted only under the current protected boundary.
    t2 = Transition("T2", 1, TRUSTED_ROOT, "V0", PROTECTED_DEPENDENCY, 11, "change_verifier", "V1")
    assert commit(state, t2, verifiers, authorities)
    state.verifier_id = "V1"
    state.verifier_dependency = "D1"
    assert state.revision == 12

    # 3. A candidate cannot replace the trust root that judges its own replacement.
    t3 = Transition("T3", 1, TRUSTED_ROOT, "V1", "D1", 12, "change_dependency", TRUSTED_ROOT)
    assert not commit(state, t3, verifiers, authorities)

    # 4. A candidate cannot replace the protected verifier boundary itself.
    t4 = Transition("T4", 1, TRUSTED_ROOT, "V1", "D1", 12, "change_verifier", PROTECTED_VERIFIER)
    assert not commit(state, t4, verifiers, authorities)

    # 5. A candidate cannot replace the protected dependency used by qualification.
    t5 = Transition("T5", 1, TRUSTED_ROOT, "V1", "D1", 12, "change_dependency", PROTECTED_DEPENDENCY)
    assert not commit(state, t5, verifiers, authorities)

    # 6. Weak verifier cannot disable its own governance guard and authorize a change.
    t6 = Transition("T6", 1, TRUSTED_ROOT, "Vweak", "D1", 12, "change_capability", "C2")
    assert not commit(state, t6, verifiers, authorities)

    # 7. Stale verifier cannot authorize a current transition.
    t7 = Transition("T7", 1, TRUSTED_ROOT, "Vstale", "D0", 12, "change_capability", "C3")
    assert not commit(state, t7, verifiers, authorities)

    # 8. Malicious verifier with a different trust root cannot authorize a transition.
    t8 = Transition("T8", 1, TRUSTED_ROOT, "Vevil", "D-EVIL", 12, "change_capability", "C4")
    assert not commit(state, t8, verifiers, authorities)

    # 9. After a legitimate epoch rotation, only the current epoch verifier can qualify.
    state.epoch = 2
    state.authority_root = TRUSTED_ROOT
    state.verifier_id = "V2"
    state.verifier_dependency = "D2"
    state.revision = 20
    t9 = Transition("T9", 2, TRUSTED_ROOT, "V2", "D2", 20, "change_capability", "C5")
    assert commit(state, t9, verifiers, authorities)

    # 10. Old-epoch verifier cannot survive the rotation.
    t10 = Transition("T10", 2, TRUSTED_ROOT, "V1", "D1", 21, "change_capability", "C6")
    assert not commit(state, t10, verifiers, authorities)

    # 11. Derived authority with an untrusted root cannot launder trust.
    authorities.add(Authority("R-DERIVED", 2))
    state.authority_root = "R-DERIVED"
    t11 = Transition("T11", 2, "R-DERIVED", "V2", "D2", 21, "change_capability", "C7")
    assert not commit(state, t11, verifiers, authorities)

    # 12. Restoring the trusted root does not restore an old revision.
    state.authority_root = TRUSTED_ROOT
    state.revision = 21
    t12 = Transition("T12", 2, TRUSTED_ROOT, "V2", "D2", 20, "change_capability", "C8")
    assert not commit(state, t12, verifiers, authorities)

    # 13. A verifier dependency mismatch cannot be used to reinterpret qualification.
    t13 = Transition("T13", 2, TRUSTED_ROOT, "V2", "D-OTHER", 21, "change_capability", "C9")
    assert not commit(state, t13, verifiers, authorities)

    # 14. The protected boundary remains external to the mutable target after valid changes.
    assert state.authority_root == TRUSTED_ROOT
    assert state.verifier_id == "V2"
    assert state.verifier_dependency == "D2"
    assert state.revision == 21

    print("P294 trust-root / verifier dependency substitution: 14/14 PASS")


if __name__ == "__main__":
    main()
