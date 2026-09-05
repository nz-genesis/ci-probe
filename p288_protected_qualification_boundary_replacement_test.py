#!/usr/bin/env python3
"""P288 — bounded protected qualification-boundary replacement probe.

Research status: executable model, not a production security proof.
The model asks whether a mutable Genesis target can replace the very
boundary that qualifies consequential self-change, including through
transitive verifier dependencies and an in-flight stale operation.
"""
from dataclasses import dataclass, replace
from typing import FrozenSet, Optional, Tuple


@dataclass(frozen=True)
class Dependency:
    name: str
    trusted_parent: Optional[str]


@dataclass(frozen=True)
class Verifier:
    name: str
    version: int
    dependency: str
    trusted_root: str
    weak: bool = False


@dataclass(frozen=True)
class Boundary:
    boundary_id: str
    root: str
    verifier_name: str
    verifier_version: int
    dependency: str
    constitutional_guard: bool = True


@dataclass(frozen=True)
class State:
    epoch: int
    authority_root: str
    verifier_name: str
    verifier_version: int
    dependency: str
    boundary_id: str


@dataclass(frozen=True)
class Transition:
    transition_id: str
    epoch: int
    authority_root: str
    verifier_name: str
    verifier_version: int
    dependency: str
    boundary_id: str
    operation: str
    target: str
    candidate_verifier_name: Optional[str] = None
    candidate_verifier_version: Optional[int] = None
    candidate_dependency: Optional[str] = None
    candidate_boundary_id: Optional[str] = None


def dependency_chain_is_trusted(name: str, dependencies: dict[str, Dependency], root: str) -> bool:
    seen: set[str] = set()
    current: Optional[str] = name
    while current is not None:
        if current in seen or current not in dependencies:
            return False
        seen.add(current)
        parent = dependencies[current].trusted_parent
        if parent is None:
            return current == root
        current = parent
    return False


def qualify(state: State, boundary: Boundary, verifier: Verifier,
            dependencies: dict[str, Dependency], t: Transition) -> bool:
    return (
        boundary.constitutional_guard
        and t.epoch == state.epoch
        and t.authority_root == state.authority_root
        and t.verifier_name == state.verifier_name
        and t.verifier_version == state.verifier_version
        and t.dependency == state.dependency
        and t.boundary_id == state.boundary_id
        and boundary.boundary_id == state.boundary_id
        and boundary.root == state.authority_root
        and boundary.verifier_name == state.verifier_name
        and boundary.verifier_version == state.verifier_version
        and boundary.dependency == state.dependency
        and verifier.name == state.verifier_name
        and verifier.version == state.verifier_version
        and verifier.dependency == state.dependency
        and verifier.trusted_root == state.authority_root
        and not verifier.weak
        and dependency_chain_is_trusted(state.dependency, dependencies, state.authority_root)
    )


def main() -> None:
    deps = {
        "ROOT-A": Dependency("ROOT-A", None),
        "dep-trusted": Dependency("dep-trusted", "ROOT-A"),
        "dep-mid": Dependency("dep-mid", "dep-trusted"),
        "dep-attacker": Dependency("dep-attacker", "ROOT-ATTACKER"),
        "ROOT-ATTACKER": Dependency("ROOT-ATTACKER", None),
    }
    boundary = Boundary("B1", "ROOT-A", "V", 1, "dep-mid")
    state = State(10, "ROOT-A", "V", 1, "dep-mid", "B1")
    verifier = Verifier("V", 1, "dep-mid", "ROOT-A")
    t = Transition("t1", 10, "ROOT-A", "V", 1, "dep-mid", "B1", "change", "capability-X")
    assert qualify(state, boundary, verifier, deps, t)

    # 1. Candidate cannot replace the protected boundary in the same change.
    assert not qualify(state, boundary, verifier, deps, replace(t, boundary_id="B2"))

    # 2. Candidate cannot replace boundary through a candidate field.
    boundary_replace = replace(t, operation="replace-boundary", candidate_boundary_id="B2")
    assert not qualify(state, boundary, verifier, deps, boundary_replace)

    # 3. Candidate verifier version cannot authorize itself.
    v2 = Verifier("V", 2, "dep-mid", "ROOT-A")
    assert not qualify(state, boundary, v2, deps, replace(t, verifier_version=2))

    # 4. Candidate dependency cannot redefine the protected chain.
    attacker_v1 = Verifier("V", 1, "dep-attacker", "ROOT-ATTACKER")
    attacker_t = replace(t, dependency="dep-attacker", authority_root="ROOT-ATTACKER")
    assert not qualify(state, boundary, attacker_v1, deps, attacker_t)

    # 5. Transitive dependency substitution is rejected.
    altered_deps = dict(deps)
    altered_deps["dep-mid"] = Dependency("dep-mid", "dep-attacker")
    assert not qualify(state, boundary, verifier, altered_deps, t)

    # 6. Dependency cycle is rejected, preventing recursive trust laundering.
    cyclic = dict(deps)
    cyclic["dep-mid"] = Dependency("dep-mid", "dep-mid")
    assert not qualify(state, boundary, verifier, cyclic, t)

    # 7. Weak verifier cannot rewrite the protected qualification semantics.
    weak = replace(verifier, weak=True)
    assert not qualify(state, boundary, weak, deps, t)

    # 8. Trust-root substitution is rejected even if verifier name/version match.
    root_swapped = replace(verifier, trusted_root="ROOT-ATTACKER")
    assert not qualify(state, boundary, root_swapped, deps, t)

    # 9. Boundary guard cannot be disabled by mutable candidate semantics.
    disabled = replace(boundary, constitutional_guard=False)
    assert not qualify(state, disabled, verifier, deps, t)

    # 10. In-flight transition qualified under old boundary becomes stale after rotation.
    rotated_state = State(11, "ROOT-A", "V", 2, "dep-mid", "B1")
    assert not qualify(rotated_state, boundary, verifier, deps, t)

    # 11. Old in-flight transition cannot be revived by swapping in the new verifier.
    assert not qualify(rotated_state, boundary, v2, deps, t)

    # 12. New verifier becomes usable only with a new, explicitly current boundary state.
    boundary2 = Boundary("B1", "ROOT-A", "V", 2, "dep-mid")
    t2 = Transition("t2", 11, "ROOT-A", "V", 2, "dep-mid", "B1", "change", "capability-Y")
    assert qualify(rotated_state, boundary2, v2, deps, t2)

    # 13. A self-authored candidate state that changes the boundary is not current.
    forged_state = State(11, "ROOT-A", "V", 2, "dep-mid", "B2")
    assert forged_state.boundary_id != state.boundary_id
    assert not qualify(rotated_state, boundary2, v2, deps, replace(t2, boundary_id="B2"))

    # 14. External protected-boundary identity cannot be inferred from the mutable target.
    foreign_boundary = Boundary("B2", "ROOT-A", "V", 2, "dep-mid")
    assert not qualify(rotated_state, foreign_boundary, v2, deps, t2)

    print("P288 protected qualification boundary replacement: 14/14 PASS")


if __name__ == "__main__":
    main()
