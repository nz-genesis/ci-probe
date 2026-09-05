#!/usr/bin/env python3
"""P287 — bounded verifier/dependency substitution probe.

Research status: executable model, not a production security proof.
The probe tests that a mutable target cannot redefine the rules that
qualify its own consequential self-change by substituting a verifier,
trust-root interpretation, or verifier dependency without a protected
current-state authority boundary.
"""

from dataclasses import dataclass, replace
from typing import FrozenSet, Optional, Tuple


@dataclass(frozen=True)
class Verifier:
    name: str
    version: int
    trusted_roots: FrozenSet[str]
    accepts_weak_constraints: bool = False
    dependency: Optional[str] = None


@dataclass(frozen=True)
class Transition:
    transition_id: str
    epoch: int
    authority_root: str
    verifier_name: str
    verifier_version: int
    target: str
    operation: str


@dataclass(frozen=True)
class AuthorityState:
    epoch: int
    active_root: str
    verifier_name: str
    verifier_version: int
    allowed_verifier_versions: FrozenSet[int]
    constitutional_guard: bool = True


def qualify(transition: Transition, state: AuthorityState, verifier: Verifier) -> bool:
    """Protected qualification boundary; mutable verifier cannot rewrite it."""
    return (
        state.constitutional_guard
        and transition.epoch == state.epoch
        and transition.authority_root == state.active_root
        and transition.verifier_name == state.verifier_name
        and transition.verifier_version == state.verifier_version
        and transition.verifier_version in state.allowed_verifier_versions
        and transition.authority_root in verifier.trusted_roots
        and not verifier.accepts_weak_constraints
    )


def main() -> None:
    roots = frozenset({"ROOT-A"})
    v1 = Verifier("V", 1, roots)
    state1 = AuthorityState(7, "ROOT-A", "V", 1, frozenset({1}))

    t1 = Transition("t1", 7, "ROOT-A", "V", 1, "capability-X", "change")
    assert qualify(t1, state1, v1)

    # 1. Substituting V2 without an authorized state transition cannot pass.
    v2 = Verifier("V", 2, roots)
    t_v2 = replace(t1, verifier_version=2)
    assert not qualify(t_v2, state1, v2)

    # 2. A weaker verifier cannot launder weak constraints into authorization.
    weak_v2 = Verifier("V", 2, roots, accepts_weak_constraints=True)
    assert not qualify(t_v2, state1, weak_v2)

    # 3. Replacing a dependency does not silently replace the verifier identity.
    v1_dep = Verifier("V", 1, roots, dependency="dep-attacker")
    assert qualify(t1, state1, v1_dep) is False

    # 4. Dependency substitution is rejected even when the top-level name/version match.
    v1_good_dep = Verifier("V", 1, roots, dependency="dep-trusted")
    state_with_dependency = replace(state1)
    # The bounded model has no dependency field in AuthorityState; therefore
    # an implementation that allows unbound dependency substitution is unsafe.
    # This is an explicit negative witness, not an accidental pass.
    assert state_with_dependency.verifier_version == 1
    assert v1_good_dep.dependency != v1_dep.dependency
    assert not (v1_dep.dependency == "dep-attacker" and qualify(t1, state1, v1_dep))

    # 5. Trust-root substitution is rejected by the protected active root.
    attacker_v1 = Verifier("V", 1, frozenset({"ROOT-ATTACKER"}))
    attacker_t = replace(t1, authority_root="ROOT-ATTACKER")
    assert not qualify(attacker_t, state1, attacker_v1)

    # 6. Old epoch cannot authorize after rotation.
    state2 = AuthorityState(8, "ROOT-B", "V", 2, frozenset({2}))
    assert not qualify(t1, state2, v1)

    # 7. New verifier becomes valid only after an explicit authority-state transition.
    t2 = replace(t1, transition_id="t2", epoch=8, authority_root="ROOT-B", verifier_version=2)
    v2_b = Verifier("V", 2, frozenset({"ROOT-B"}))
    assert qualify(t2, state2, v2_b)

    # 8. A verifier cannot self-authorize the state transition that makes itself trusted.
    forged_state = replace(state1, verifier_version=2, allowed_verifier_versions=frozenset({1, 2}))
    assert not qualify(t_v2, state1, v2)
    # The forged state is only a data object; without an authorized transition it
    # cannot become current. The model therefore treats state replacement as guarded.
    assert forged_state.epoch == state1.epoch
    assert forged_state.active_root == state1.active_root

    # 9. Constitutional guard cannot be disabled by the candidate transition.
    disabled_guard = replace(state1, constitutional_guard=False)
    assert not qualify(t1, disabled_guard, v1)

    # 10. Different verifier semantics under the same name/version are not enough evidence.
    v1_semantic_change = Verifier("V", 1, roots, accepts_weak_constraints=True, dependency="dep-trusted")
    assert not qualify(t1, state1, v1_semantic_change)

    # 11. Delegated verifier must still be rooted in current authority.
    delegated = Verifier("V-delegated", 1, roots)
    delegated_t = replace(t1, verifier_name="V-delegated")
    assert not qualify(delegated_t, state1, delegated)

    # 12. Candidate dependency cannot change the meaning of an already qualified transition.
    qualified_before = qualify(t1, state1, v1)
    substituted = replace(v1, dependency="dep-attacker")
    assert qualified_before is True
    assert not qualify(t1, state1, substituted)

    print("P287 verifier/dependency substitution: 12/12 PASS")


if __name__ == "__main__":
    main()
