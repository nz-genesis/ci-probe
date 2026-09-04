"""Executable falsification harness for recursive governed self-change.

This is a semantic probe, not a Genesis implementation. It checks that a system
can change a capability and even propose a change to its change mechanism
without allowing the changed mechanism to self-authorize privilege escalation,
weaken verification, or alter constitutional invariants.
"""

from dataclasses import dataclass, replace
from enum import Enum


class Target(Enum):
    CAPABILITY = "capability"
    CHANGE_MECHANISM = "change_mechanism"
    AUTHORITY = "authority"
    PURPOSE = "purpose"


@dataclass(frozen=True)
class Constitution:
    purpose_hash: str
    protected_authority: bool = True
    protected_verifier: bool = True


@dataclass(frozen=True)
class State:
    generation: int
    capability_version: int
    mechanism_version: int
    authority_version: int
    constitution: Constitution


@dataclass(frozen=True)
class Candidate:
    target: Target
    requested_generation: int
    requested_capability_version: int | None = None
    requested_mechanism_version: int | None = None
    requested_authority_version: int | None = None
    requested_purpose_hash: str | None = None
    evidence_fresh: bool = True
    verifier_independent: bool = True
    human_approved: bool = False


def qualify(candidate: Candidate, state: State) -> bool:
    if candidate.requested_generation != state.generation:
        return False
    if not candidate.evidence_fresh or not candidate.verifier_independent:
        return False

    # Constitutional targets cannot be self-authorized.
    if candidate.target in {Target.AUTHORITY, Target.PURPOSE}:
        return candidate.human_approved

    # A change to the change mechanism may not disable its own guardrails.
    if candidate.target is Target.CHANGE_MECHANISM:
        return candidate.human_approved

    return True


def apply(candidate: Candidate, state: State) -> State:
    assert qualify(candidate, state), "inadmissible candidate must not execute"

    if candidate.target is Target.CAPABILITY:
        return replace(
            state,
            generation=state.generation + 1,
            capability_version=candidate.requested_capability_version
            or state.capability_version + 1,
        )

    if candidate.target is Target.CHANGE_MECHANISM:
        # Even an approved change cannot silently mutate constitutional guards.
        return replace(
            state,
            generation=state.generation + 1,
            mechanism_version=candidate.requested_mechanism_version
            or state.mechanism_version + 1,
        )

    if candidate.target is Target.AUTHORITY:
        return replace(
            state,
            generation=state.generation + 1,
            authority_version=candidate.requested_authority_version
            or state.authority_version + 1,
        )

    return replace(
        state,
        generation=state.generation + 1,
        constitution=replace(
            state.constitution,
            purpose_hash=candidate.requested_purpose_hash
            or state.constitution.purpose_hash,
        ),
    )


def test_capability_self_evolution_is_expressible() -> None:
    s0 = initial_state()
    c1 = Candidate(Target.CAPABILITY, s0.generation, requested_capability_version=2)
    s1 = apply(c1, s0)
    assert s1.capability_version == 2
    assert s1.constitution == s0.constitution


def test_change_mechanism_requires_external_governance() -> None:
    s0 = initial_state()
    c = Candidate(Target.CHANGE_MECHANISM, s0.generation, requested_mechanism_version=2)
    assert not qualify(c, s0)
    c_approved = replace(c, human_approved=True)
    s1 = apply(c_approved, s0)
    assert s1.mechanism_version == 2
    assert s1.constitution == s0.constitution


def test_recursive_escalation_cannot_authorize_itself() -> None:
    s0 = initial_state()
    c1 = replace(
        Candidate(Target.CHANGE_MECHANISM, s0.generation, requested_mechanism_version=2),
        human_approved=True,
    )
    s1 = apply(c1, s0)

    # The new mechanism cannot use its own new generation to bypass approval.
    c2 = Candidate(Target.AUTHORITY, s1.generation, requested_authority_version=2)
    assert not qualify(c2, s1)

    c3 = Candidate(
        Target.PURPOSE,
        s1.generation,
        requested_purpose_hash="attacker-purpose",
    )
    assert not qualify(c3, s1)


def test_stale_evidence_cannot_authorize_recursive_change() -> None:
    s0 = initial_state()
    stale = Candidate(
        Target.CHANGE_MECHANISM,
        s0.generation,
        requested_mechanism_version=2,
        evidence_fresh=False,
        human_approved=True,
    )
    assert not qualify(stale, s0)


def initial_state() -> State:
    return State(
        generation=0,
        capability_version=1,
        mechanism_version=1,
        authority_version=1,
        constitution=Constitution(purpose_hash="genesis-purpose-v1"),
    )


def run() -> None:
    test_capability_self_evolution_is_expressible()
    test_change_mechanism_requires_external_governance()
    test_recursive_escalation_cannot_authorize_itself()
    test_stale_evidence_cannot_authorize_recursive_change()
    print("recursive governed change: PASS")


if __name__ == "__main__":
    run()
