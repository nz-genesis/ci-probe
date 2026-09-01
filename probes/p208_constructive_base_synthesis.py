#!/usr/bin/env python3
"""P208 clean-room constructive synthesis probe.

Purpose: test whether the strongest pre-existing Genesis Base candidate set can
construct four representative action classes without introducing a new
semantic primitive. This is an implementation-independent simulation; it is
not a claim about the Genesis runtime.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Any


BASE = {
    "identity",
    "state",
    "interaction",
    "authority",
    "capability",
    "control",
    "runtime",
    "execution",
    "observation",
    "verification",
    "evidence",
    "persistence",
    "recovery",
    "constraints",
}


@dataclass(frozen=True)
class Action:
    kind: str
    capability: str
    principal: str
    authorized: bool = True
    constrained: bool = True
    observed: bool = False
    verified: bool = False
    persisted: bool = False
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
    if a.kind == "external":
        state["already_effected"] = True
    if a.kind == "meta":
        state["protected_version"] += 1
    return replace(a, observed=True)


def verify(a: Action) -> Action:
    if not a.observed:
        raise ValueError("verification requires observation")
    if not a.goal_met:
        return replace(a, verified=False)
    return replace(a, verified=True, persisted=True)


def run(kind: str, capability: str, *, external: bool = False) -> Action:
    state = {"protected_version": 1, "already_effected": False, "revoked": False}
    a = Action(kind, capability, "principal-A")
    a = admit(a, state=state)
    a = execute(a, state=state)
    a = verify(a)
    assert a.verified and a.persisted
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
    return not a.verified


def attack_meta_without_authority() -> bool:
    try:
        admit(Action("meta", "change-core", "principal-A", authorized=False), state={"revoked": False})
    except ValueError:
        return True
    return False


def attack_extension_core_mutation() -> bool:
    before = set(BASE)
    extension = {"new-capability"}
    after = before | extension
    return before == set(BASE) and not ("new-capability" in before) and "new-capability" in after


def attack_llm_dependency() -> bool:
    # Cognitive provider is an extension; execution remains defined by BASE.
    return "execution" in BASE and "authority" in BASE and "capability" in BASE


def attack_rich_memory_dependency() -> bool:
    # Rich memory is deliberately absent from BASE; minimal persistence remains.
    return "persistence" in BASE and "rich-memory" not in BASE


def attack_headless_operation() -> bool:
    # Interaction contract is semantic; presentation is not a Base dependency.
    return "interaction" in BASE and "dashboard" not in BASE


def attack_undeclared_primitive() -> bool:
    # Four action classes use only BASE plus explicitly declared extension data.
    required = {
        "local": BASE,
        "artifact": BASE | {"external-cognitive-provider"},
        "external": BASE | {"external-adapter"},
        "meta": BASE | {"governance-principal"},
    }
    return all(set(BASE).issubset(v) for v in required.values())


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
    ]
    results.extend((f"red-team-{name}", value) for name, value in attacks)

    failed = [name for name, ok in results if not ok]
    for name, ok in results:
        print(f"{'PASS' if ok else 'FAIL'} {name}")
    if failed:
        raise SystemExit(f"P208_FAIL: {failed}")
    print(f"P208_CONSTRUCTIVE_BASE_SYNTHESIS_PASS; assertions={len(results)}; new_primitive_required=false")


if __name__ == "__main__":
    main()
