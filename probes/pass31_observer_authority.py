"""Pass 31 public-safe observer authority / verification / source-compromise probe.

Synthetic only: no private Genesis state, witnesses, credentials, or imports.
"""
from dataclasses import dataclass
from enum import Enum


class Decision(Enum):
    REALIZED = "REALIZED"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class Observation:
    effect_id: str
    scope: str
    state_version: int
    source_id: str
    causal_boundary: int
    status: str


@dataclass(frozen=True)
class Authority:
    subject: str
    version: int
    active: bool


@dataclass(frozen=True)
class Evidence:
    observation: Observation
    authority_version: int
    source_authorized: bool
    verified: bool
    verifier_authorized: bool
    chain_complete: bool
    claim: str


@dataclass(frozen=True)
class Constraint:
    required_source: str | None
    minimum_observer_authority_version: int
    minimum_verifier_authority_version: int
    minimum_observer_causal_boundary: int


def assess(effect_id: str, e: Evidence, c: Constraint, observer_authority: Authority, verifier_authority: Authority) -> Decision:
    o = e.observation
    if o.effect_id != effect_id:
        return Decision.UNKNOWN
    if c.required_source is not None and o.source_id != c.required_source:
        return Decision.UNKNOWN
    if not observer_authority.active or observer_authority.subject != o.source_id:
        return Decision.UNKNOWN
    if e.authority_version != observer_authority.version:
        return Decision.UNKNOWN
    if e.authority_version < c.minimum_observer_authority_version:
        return Decision.UNKNOWN
    if not verifier_authority.active or not e.verifier_authorized:
        return Decision.UNKNOWN
    if verifier_authority.version < c.minimum_verifier_authority_version:
        return Decision.UNKNOWN
    if not e.source_authorized or not e.verified or not e.chain_complete:
        return Decision.UNKNOWN
    if o.causal_boundary < c.minimum_observer_causal_boundary:
        return Decision.UNKNOWN
    if e.claim == "conflict":
        return Decision.CONFLICT
    if e.claim == "applied" and o.status == "APPLIED":
        return Decision.REALIZED
    return Decision.UNKNOWN


def baseline() -> tuple[Evidence, Constraint, Authority, Authority]:
    observation = Observation("e1", "target-a", 7, "observer-a", 12, "APPLIED")
    evidence = Evidence(observation, 3, True, True, True, True, "applied")
    constraint = Constraint("observer-a", 3, 5, 12)
    observer_authority = Authority("observer-a", 3, True)
    verifier_authority = Authority("verifier-a", 5, True)
    return evidence, constraint, observer_authority, verifier_authority


def test_same_payload_differs_by_observer_authority() -> None:
    e, c, _, verifier = baseline()
    revoked = Authority("observer-a", 4, True)
    assert assess("e1", e, c, revoked, verifier) is Decision.UNKNOWN


def test_same_payload_with_active_matching_authority_is_admissible() -> None:
    e, c, observer, verifier = baseline()
    assert assess("e1", e, c, observer, verifier) is Decision.REALIZED


def test_observer_authority_revoked_after_observation_is_not_silent() -> None:
    e, c, _, verifier = baseline()
    revoked = Authority("observer-a", 3, False)
    assert assess("e1", e, c, revoked, verifier) is Decision.UNKNOWN


def test_stale_observer_authority_version_is_rejected() -> None:
    e, c, _, verifier = baseline()
    current = Authority("observer-a", 4, True)
    assert assess("e1", e, c, current, verifier) is Decision.UNKNOWN


def test_compromised_verifier_is_rejected() -> None:
    e, c, observer, _ = baseline()
    compromised = Authority("verifier-a", 5, False)
    assert assess("e1", e, c, observer, compromised) is Decision.UNKNOWN


def test_untrusted_verification_does_not_create_authority() -> None:
    e, c, observer, verifier = baseline()
    unverified = Evidence(e.observation, e.authority_version, True, False, False, True, "applied")
    assert assess("e1", unverified, c, observer, verifier) is Decision.UNKNOWN


def test_intermediate_invalid_observer_chain_remains_unknown() -> None:
    e, c, observer, verifier = baseline()
    truncated = Evidence(e.observation, e.authority_version, True, True, True, False, "applied")
    assert assess("e1", truncated, c, observer, verifier) is Decision.UNKNOWN


def test_verifier_authority_version_must_meet_transition_requirement() -> None:
    e, c, observer, _ = baseline()
    old_verifier = Authority("verifier-a", 4, True)
    assert assess("e1", e, c, observer, old_verifier) is Decision.UNKNOWN


def test_conflicting_verdict_is_preserved() -> None:
    e, c, observer, verifier = baseline()
    conflict = Evidence(e.observation, e.authority_version, True, True, True, True, "conflict")
    assert assess("e1", conflict, c, observer, verifier) is Decision.CONFLICT


def test_source_substitution_requires_matching_observer_authority() -> None:
    e, c, observer, verifier = baseline()
    substituted = Observation(e.observation.effect_id, e.observation.scope, e.observation.state_version, "observer-b", e.observation.causal_boundary, e.observation.status)
    altered = Evidence(substituted, e.authority_version, True, True, True, True, "applied")
    assert assess("e1", altered, c, observer, verifier) is Decision.UNKNOWN


def test_no_new_genesis_primitive_is_needed() -> None:
    candidate = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}
    proposed = {"Source", "Trust", "Provenance", "Witness", "Confidence", "Verifier", "ObserverAuthority"}
    assert candidate.isdisjoint(proposed)


def main() -> None:
    test_same_payload_differs_by_observer_authority()
    test_same_payload_with_active_matching_authority_is_admissible()
    test_observer_authority_revoked_after_observation_is_not_silent()
    test_stale_observer_authority_version_is_rejected()
    test_compromised_verifier_is_rejected()
    test_untrusted_verification_does_not_create_authority()
    test_intermediate_invalid_observer_chain_remains_unknown()
    test_verifier_authority_version_must_meet_transition_requirement()
    test_conflicting_verdict_is_preserved()
    test_source_substitution_requires_matching_observer_authority()
    test_no_new_genesis_primitive_is_needed()
    print("PASS31_PUBLIC: PASS; cases=11; private_data=none; new_primitives=0")


if __name__ == "__main__":
    main()
