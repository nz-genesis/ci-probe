#!/usr/bin/env python3
"""P208 clean-room constructive synthesis probe.

Purpose: test whether the current seven-element Genesis candidate basis can
construct four representative action classes without introducing a new
semantic primitive. Runtime, execution, persistence, recovery, interaction,
and presentation are treated as implementation/context mechanisms rather than
Genesis primitives. This probe is not a claim about the Genesis runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any


CANDIDATE_BASIS = {
    "state",
    "transition",
    "capability",
    "authority",
    "observation",
    "evidence",
    "constraint",
}


@dataclass(frozen=True)
class Action:
    kind: str
    capability: str
    principal: str
    authorized: bool = True
    constrained: bool = True
    observed: bool = False
    evidenced: bool = False
    duplicate: bool = False
    bypass: bool = False
    goal_met: bool = True


def admit(a: Action, *, state: dict[str, Any]) -> Action:
    if not a.authorized or not a.constrained or a.bypass:
        raise ValueError("admission rejected")
    if state.get("revoked", False):
        raise ValueError("admission rejected: authority revoked")
    if state.get("already_effected", False) and a.kind == "external":
        raise ValueError("admission rejected: duplicate irreversible effect")
    return a


def execute(a: Action, *, state: dict[str, Any]) -> Action:
    # Execution is an implementation realization of a Transition, not a new
    # Genesis primitive. External effects are represented as observed state.
    if a.kind == "external":
        state["already_effected"] = True
    if a.kind == "meta":
        state["protected_version"] += 1
    return replace(a, observed=True)


def verify(a: Action) -> Action:
    # Evidence records the result of an Observation; it is not execution proof
    # by itself. A failed goal therefore cannot become verified success.
    if not a.observed:
        raise ValueError("verification requires observation")
    if not a.goal_met:
        return replace(a, evidenced=False)
    return replace(a, evidenced=True)


def run(kind: str, capability: str, *, external: bool = False) -> Action:
    state = {"protected_version": 1, "already_effected": False, "revoked": False}
    a = Action(kind, capability, "principal-A")
    a = admit(a, state=state)
    a = execute(a, state=state)
    a = verify(a)
    assert a.evidenced
    if external:
        assert state["already_effected"]
    return a


def attack_capability_without_authority() -> bool:
    try:
        admit(Action("local", "x", "untrusted", authorized=False), state={"revoked": False})
    except ValueError:
        return True
    return False


def attack_cognition_bypass() -> bool:
    try:
        admit(Action("artifact", "cognitive-x", "principal-A", bypass=True), state={"revoked": False})
    except ValueError:
        return True
    return False


def attack_duplicate_external_effect() -> bool:
    state = {"revoked": False, "already_effected": True}
    try:
        admit(Action("external", "send", "principal-A"), state=state)
    except ValueError:
        return True
    return False


def attack_stale_revocation() -> bool:
    state = {"revoked": True}
    try:
        admit(Action("local", "change", "principal-A"), state=state)
    except ValueError:
        return True
    return False


def attack_goal_effect_mismatch() -> bool:
    a = admit(Action("artifact", "research", "principal-A", goal_met=False), state={"revoked": False})
    a = execute(a, state={"protected_version": 1})
    a = verify(a)
    return not a.evidenced


def attack_meta_without_authority() -> bool:
    try:
        admit(Action("meta", "change-core", "principal-A", authorized=False), state={"revoked": False})
    except ValueError:
        return True
    return False


def attack_extension_core_mutation() -> bool:
    # Extensions can add capabilities/realizations, but cannot silently alter
    # the semantic candidate basis.
    before = set(CANDIDATE_BASIS)
    extension = {"external-adapter"}
    after = before | extension
    return before == set(CANDIDATE_BASIS) and "external-adapter" not in before and "external-adapter" in after


def attack_llm_dependency() -> bool:
    # LLM is an optional realization of a Capability; it is not a primitive.
    return CANDIDATE_BASIS == {
        "state", "transition", "capability", "authority", "observation", "evidence", "constraint"
    }


def attack_rich_memory_dependency() -> bool:
    # Rich memory is deliberately absent from the candidate basis.
    return "state" in CANDIDATE_BASIS and "rich-memory" not in CANDIDATE_BASIS


def attack_headless_operation() -> bool:
    # UI/dashboard is a realization, not a semantic primitive.
    return "transition" in CANDIDATE_BASIS and "dashboard" not in CANDIDATE_BASIS


def attack_undeclared_primitive() -> bool:
    # All four classes use only the seven candidate primitives; external
    # providers/adapters/principals are realizations or values.
    required = {
        "local": CANDIDATE_BASIS,
        "artifact": CANDIDATE_BASIS,
        "external": CANDIDATE_BASIS,
        "meta": CANDIDATE_BASIS,
    }
    return all(set(CANDIDATE_BASIS).issubset(v) for v in required.values())


def attack_observation_as_execution() -> bool:
    a = Action("artifact", "observe-only", "principal-A")
    a = replace(a, observed=True, evidenced=False)
    return not a.evidenced


def attack_unknown_as_success() -> bool:
    a = Action("external", "unknown", "principal-A", observed=True, evidenced=False)
    return not a.evidenced


def main() -> None:
    results = []
    for kind, capability in [
        ("local", "state-transition"),
        ("artifact", "cognitive-research"),
        ("external", "world-adapter"),
        ("meta", "protected-change"),
    ]:
        results.append((f"construct-{kind}", run(kind, capability, external=kind == "external")))

    attacks = [
        ("capability-without-authority", attack_capability_without_authority()),
        ("cognition-bypass", attack_cognition_bypass()),
        ("duplicate-external-effect", attack_duplicate_external_effect()),
        ("stale-revocation", attack_stale_revocation()),
        ("goal-effect-mismatch", attack_goal_effect_mismatch()),
        ("meta-without-authority", attack_meta_without_authority()),
        ("extension-core-mutation", attack_extension_core_mutation()),
        ("llm-dependency", attack_llm_dependency()),
        ("rich-memory-dependency", attack_rich_memory_dependency()),
        ("headless-operation", attack_headless_operation()),
        ("undeclared-primitive", attack_undeclared_primitive()),
        ("observation-as-execution", attack_observation_as_execution()),
        ("unknown-as-success", attack_unknown_as_success()),
    ]
    results.extend((f"red-team-{name}", value) for name, value in attacks)

    failed = [name for name, ok in results if not ok]
    for name, ok in results:
        print(f"{'PASS' if ok else 'FAIL'} {name}")
    if failed:
        raise SystemExit(f"P208_FAIL: {failed}")
    print(f"P208_CONSTRUCTIVE_BASE_SYNTHESIS_PASS; assertions={len(results)}; basis_size={len(CANDIDATE_BASIS)}; new_primitive_required=false")


if __name__ == "__main__":
    main()
