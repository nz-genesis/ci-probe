"""Executable falsification harness for recursive governed self-change.

This is a bounded semantic probe, not a Genesis implementation. It checks that
self-change remains governed across generations, in-flight work, delegation,
cache reuse, and recovery, while protected governance boundaries remain closed.
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
    verifier_version: int
    constitution: Constitution


@dataclass(frozen=True)
class Candidate:
    target: Target
    requested_generation: int
    requested_capability_version: int | None = None
    requested_mechanism_version: int | None = None
    requested_authority_version: int | None = None
    requested_verifier_version: int | None = None
    requested_purpose_hash: str | None = None
    disable_authority_guard: bool = False
    disable_verifier_guard: bool = False
    evidence_fresh: bool = True
    verifier_independent: bool = True
    human_approved: bool = False


@dataclass(frozen=True)
class AuthorityToken:
    issued_generation: int
    scope: Target
    independent: bool = True


@dataclass(frozen=True)
class InFlightAction:
    bound_generation: int
    bound_capability_version: int
    authority: AuthorityToken


@dataclass(frozen=True)
class CacheEntry:
    generation: int
    capability_version: int
    value: str


@dataclass(frozen=True)
class ExternalEffect:
    action_id: str
    committed: bool


def qualify(candidate: Candidate, state: State) -> bool:
    if candidate.requested_generation != state.generation:
        return False
    if not candidate.evidence_fresh or not candidate.verifier_independent:
        return False

    if candidate.target in {
        Target.AUTHORITY,
        Target.PURPOSE,
        Target.CHANGE_MECHANISM,
    }:
        if not candidate.human_approved:
            return False

    if candidate.target is Target.CHANGE_MECHANISM:
        if candidate.disable_authority_guard or candidate.disable_verifier_guard:
            return False

    return True


def apply(candidate: Candidate, state: State) -> State:
    assert qualify(candidate, state), "inadmissible candidate must not execute"

    if candidate.target is Target.CAPABILITY:
        return replace(
            state,
            generation=state.generation + 1,
            capability_version=(
                candidate.requested_capability_version
                if candidate.requested_capability_version is not None
                else state.capability_version + 1
            ),
        )

    if candidate.target is Target.CHANGE_MECHANISM:
        return replace(
            state,
            generation=state.generation + 1,
            mechanism_version=(
                candidate.requested_mechanism_version
                if candidate.requested_mechanism_version is not None
                else state.mechanism_version + 1
            ),
            verifier_version=(
                candidate.requested_verifier_version
                if candidate.requested_verifier_version is not None
                else state.verifier_version
            ),
        )

    if candidate.target is Target.AUTHORITY:
        return replace(
            state,
            generation=state.generation + 1,
            authority_version=(
                candidate.requested_authority_version
                if candidate.requested_authority_version is not None
                else state.authority_version + 1
            ),
        )

    return replace(
        state,
        generation=state.generation + 1,
        constitution=replace(
            state.constitution,
            purpose_hash=(
                candidate.requested_purpose_hash
                if candidate.requested_purpose_hash is not None
                else state.constitution.purpose_hash
            ),
        ),
    )


def issue_authority(state: State, scope: Target) -> AuthorityToken:
    return AuthorityToken(issued_generation=state.generation, scope=scope)


def can_delegate(token: AuthorityToken, requested_scope: Target, state: State) -> bool:
    # Delegation cannot outlive its issuing generation or widen its scope.
    return (
        token.independent
        and token.issued_generation == state.generation
        and requested_scope is token.scope
        and requested_scope not in {Target.AUTHORITY, Target.PURPOSE}
    )


def bind_action(state: State, token: AuthorityToken) -> InFlightAction:
    assert token.issued_generation == state.generation
    return InFlightAction(
        bound_generation=state.generation,
        bound_capability_version=state.capability_version,
        authority=token,
    )


def finish_action(action: InFlightAction, state: State) -> bool:
    # A generation change does not rewrite an already-authorized action.
    return (
        action.authority.issued_generation == action.bound_generation
        and action.bound_capability_version >= 1
        and action.authority.scope is Target.CAPABILITY
    )


def cache_usable(entry: CacheEntry, state: State) -> bool:
    # Cache may accelerate cognition, but cannot silently cross a generation.
    return (
        entry.generation == state.generation
        and entry.capability_version == state.capability_version
    )


def recover_effect(effect: ExternalEffect) -> ExternalEffect:
    # Bounded model: failed/uncommitted effects are not treated as committed.
    return replace(effect, committed=False)


def initial_state() -> State:
    return State(
        generation=0,
        capability_version=1,
        mechanism_version=1,
        authority_version=1,
        verifier_version=1,
        constitution=Constitution(purpose_hash="genesis-purpose-v1"),
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
    assert s1.verifier_version == s0.verifier_version


def test_approved_mechanism_change_cannot_remove_guards() -> None:
    s0 = initial_state()
    malicious = Candidate(
        Target.CHANGE_MECHANISM,
        s0.generation,
        requested_mechanism_version=2,
        disable_authority_guard=True,
        disable_verifier_guard=True,
        human_approved=True,
    )
    assert not qualify(malicious, s0)


def test_recursive_escalation_cannot_authorize_itself() -> None:
    s0 = initial_state()
    c1 = replace(
        Candidate(Target.CHANGE_MECHANISM, s0.generation, requested_mechanism_version=2),
        human_approved=True,
    )
    s1 = apply(c1, s0)
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


def test_inflight_action_keeps_original_binding() -> None:
    s0 = initial_state()
    token = issue_authority(s0, Target.CAPABILITY)
    action = bind_action(s0, token)
    s1 = apply(Candidate(Target.CAPABILITY, s0.generation, requested_capability_version=2), s0)
    assert action.bound_generation == 0
    assert action.bound_capability_version == 1
    assert finish_action(action, s1)


def test_delegation_cannot_cross_generation_or_widen_scope() -> None:
    s0 = initial_state()
    token = issue_authority(s0, Target.CAPABILITY)
    assert can_delegate(token, Target.CAPABILITY, s0)
    assert not can_delegate(token, Target.AUTHORITY, s0)
    s1 = apply(Candidate(Target.CAPABILITY, s0.generation, requested_capability_version=2), s0)
    assert not can_delegate(token, Target.CAPABILITY, s1)


def test_cache_cannot_cross_generation() -> None:
    s0 = initial_state()
    entry = CacheEntry(s0.generation, s0.capability_version, "qualified-result")
    assert cache_usable(entry, s0)
    s1 = apply(Candidate(Target.CAPABILITY, s0.generation, requested_capability_version=2), s0)
    assert not cache_usable(entry, s1)


def test_recovery_does_not_relabel_uncommitted_external_effect() -> None:
    failed = ExternalEffect(action_id="a1", committed=False)
    recovered = recover_effect(failed)
    assert not recovered.committed


def run() -> None:
    test_capability_self_evolution_is_expressible()
    test_change_mechanism_requires_external_governance()
    test_approved_mechanism_change_cannot_remove_guards()
    test_recursive_escalation_cannot_authorize_itself()
    test_stale_evidence_cannot_authorize_recursive_change()
    test_inflight_action_keeps_original_binding()
    test_delegation_cannot_cross_generation_or_widen_scope()
    test_cache_cannot_cross_generation()
    test_recovery_does_not_relabel_uncommitted_external_effect()
    print("recursive governed change: PASS")


if __name__ == "__main__":
    run()
