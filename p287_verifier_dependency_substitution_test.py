#!/usr/bin/env python3
"""P287 — bounded verifier/dependency substitution probe.

Research status: executable model, not a production security proof.
"""
from dataclasses import dataclass, replace
from typing import FrozenSet, Optional

@dataclass(frozen=True)
class Verifier:
    name: str
    version: int
    trusted_roots: FrozenSet[str]
    dependency: Optional[str] = None
    accepts_weak_constraints: bool = False

@dataclass(frozen=True)
class Transition:
    transition_id: str
    epoch: int
    authority_root: str
    verifier_name: str
    verifier_version: int
    dependency: str
    target: str
    operation: str

@dataclass(frozen=True)
class AuthorityState:
    epoch: int
    active_root: str
    verifier_name: str
    verifier_version: int
    dependency: str
    allowed_verifier_versions: FrozenSet[int]
    constitutional_guard: bool = True

def qualify(t: Transition, s: AuthorityState, v: Verifier) -> bool:
    return (
        s.constitutional_guard
        and t.epoch == s.epoch
        and t.authority_root == s.active_root
        and t.verifier_name == s.verifier_name
        and t.verifier_version == s.verifier_version
        and t.verifier_version in s.allowed_verifier_versions
        and t.dependency == s.dependency
        and v.name == s.verifier_name
        and v.version == s.verifier_version
        and v.dependency == s.dependency
        and t.authority_root in v.trusted_roots
        and not v.accepts_weak_constraints
    )

def main() -> None:
    roots_a = frozenset({"ROOT-A"})
    v1 = Verifier("V", 1, roots_a, dependency="dep-trusted")
    state1 = AuthorityState(7, "ROOT-A", "V", 1, "dep-trusted", frozenset({1}))
    t1 = Transition("t1", 7, "ROOT-A", "V", 1, "dep-trusted", "capability-X", "change")
    assert qualify(t1, state1, v1)

    # 1. Version substitution without an authorized state transition.
    v2 = Verifier("V", 2, roots_a, dependency="dep-trusted")
    assert not qualify(replace(t1, verifier_version=2), state1, v2)

    # 2. Weaker verifier cannot launder weak constraints.
    weak_v1 = replace(v1, accepts_weak_constraints=True)
    assert not qualify(t1, state1, weak_v1)

    # 3. Dependency substitution cannot pass with the same verifier identity.
    attacker_dep_v1 = replace(v1, dependency="dep-attacker")
    attacker_dep_t = replace(t1, dependency="dep-attacker")
    assert not qualify(attacker_dep_t, state1, attacker_dep_v1)

    # 4. Current state explicitly binds the dependency.
    assert attacker_dep_v1.dependency != state1.dependency
    assert not qualify(t1, state1, attacker_dep_v1)

    # 5. Trust-root substitution cannot manufacture current authority.
    attacker_root_v1 = replace(v1, trusted_roots=frozenset({"ROOT-ATTACKER"}))
    attacker_root_t = replace(t1, authority_root="ROOT-ATTACKER")
    assert not qualify(attacker_root_t, state1, attacker_root_v1)

    # 6. Old epoch cannot authorize after rotation.
    state2 = AuthorityState(8, "ROOT-B", "V", 2, "dep-v2", frozenset({2}))
    assert not qualify(t1, state2, v1)

    # 7. New verifier is valid only under the new explicit authority state.
    v2_b = Verifier("V", 2, frozenset({"ROOT-B"}), dependency="dep-v2")
    t2 = Transition("t2", 8, "ROOT-B", "V", 2, "dep-v2", "capability-X", "change")
    assert qualify(t2, state2, v2_b)

    # 8. A candidate verifier cannot self-authorize the state that trusts it.
    forged_state = replace(state1, verifier_version=2, allowed_verifier_versions=frozenset({1, 2}))
    assert not qualify(replace(t1, verifier_version=2), state1, v2)
    assert forged_state.verifier_version == 2
    assert state1.verifier_version == 1

    # 9. Constitutional guard is outside the candidate's mutable semantics.
    disabled_guard = replace(state1, constitutional_guard=False)
    assert not qualify(t1, disabled_guard, v1)

    # 10. Same identity/version with changed semantics is not sufficient evidence.
    semantic_change = replace(v1, accepts_weak_constraints=True)
    assert not qualify(t1, state1, semantic_change)

    # 11. Delegated verifier cannot replace the current verifier identity implicitly.
    delegated = Verifier("V-delegated", 1, roots_a, dependency="dep-trusted")
    assert not qualify(replace(t1, verifier_name="V-delegated"), state1, delegated)

    # 12. A dependency mutation after qualification invalidates current qualification.
    assert qualify(t1, state1, v1) is True
    substituted = replace(v1, dependency="dep-attacker")
    assert not qualify(t1, state1, substituted)

    print("P287 verifier/dependency substitution: 12/12 PASS")

if __name__ == "__main__":
    main()
