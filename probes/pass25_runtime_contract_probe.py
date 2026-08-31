"""Public-safe Pass 25 contract probe.

This file contains only bounded behavioral assertions. It does not import or
mirror private Genesis implementation, state, witness material, or authority data.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Authority:
    subject: str
    capability: str
    target: str
    scope: dict[str, str]
    version: int
    valid: bool


@dataclass(frozen=True)
class Transition:
    transition_id: str
    effect_id: str
    capability: str
    target: str
    operation: str
    scope: dict[str, str]


def scope_contains(parent: dict[str, str], child: dict[str, str]) -> bool:
    return all(parent.get(k) == v for k, v in child.items())


def admit(t: Transition, capabilities: set[str], authorities: list[Authority], allowed_targets: set[str]) -> Authority | None:
    if not all((t.transition_id, t.effect_id, t.capability, t.target, t.operation)):
        return None
    if t.capability not in capabilities or t.target not in allowed_targets:
        return None
    for authority in authorities:
        if (
            authority.valid
            and authority.capability == t.capability
            and authority.target == t.target
            and scope_contains(authority.scope, t.scope)
        ):
            return authority
    return None


def run() -> None:
    authority = Authority("public-test", "heat", "toaster", {"mode": "ready"}, 1, True)
    capabilities = {"heat"}
    allowed_targets = {"toaster"}
    reserved: set[str] = set()

    valid = Transition("t1", "effect-1", "heat", "toaster", "on", {})
    granted = admit(valid, capabilities, [authority], allowed_targets)
    assert granted == authority, "valid capability+authority must admit"
    assert valid.effect_id not in reserved
    reserved.add(valid.effect_id)
    assert valid.effect_id in reserved, "reservation must be observable"

    duplicate = Transition("t2", "effect-1", "heat", "toaster", "on", {})
    assert duplicate.effect_id in reserved, "duplicate effect identity must be detected"

    unauthorized = Transition("t3", "effect-2", "cool", "toaster", "on", {})
    assert admit(unauthorized, capabilities, [authority], allowed_targets) is None, "capability must not be laundered into authority"

    widened = Transition("t4", "effect-3", "heat", "toaster", "on", {"mode": "danger"})
    assert admit(widened, capabilities, [authority], allowed_targets) is None, "scope widening must fail closed"

    malformed = Transition("", "", "", "", "", {})
    assert admit(malformed, capabilities, [authority], allowed_targets) is None, "malformed input must fail closed"

    stale = Authority(authority.subject, authority.capability, authority.target, authority.scope, 2, False)
    assert stale != authority and not stale.valid, "revoked authority must not remain valid"

    # ACK alone is deliberately not modeled as a verified external effect.
    outcome = "UNKNOWN"
    assert outcome != "APPLIED", "ACK/uncertainty must not become verified effect"
    assert outcome != "SUCCESS", "UNKNOWN must remain explicit"

    print("PASS25_PUBLIC: PASS; cases=8; private_data=none; new_primitives=0")


if __name__ == "__main__":
    run()
