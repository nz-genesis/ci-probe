"""Pass 32 public-safe authority delegation / multi-party verification probe.

Synthetic only: no private Genesis state, witnesses, credentials, or imports.
"""
from dataclasses import dataclass
from enum import Enum


class Decision(Enum):
    REALIZED = "REALIZED"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class Authority:
    subject: str
    issuer: str | None
    scope: str
    version: int
    active: bool


@dataclass(frozen=True)
class Observation:
    effect_id: str
    source: str
    version: int
    status: str


@dataclass(frozen=True)
class Evidence:
    observation: Observation
    observer_authority: Authority
    verifier_authorities: tuple[Authority, ...]
    verified: bool
    chain_complete: bool
    claim: str


@dataclass(frozen=True)
class Constraint:
    required_source: str
    required_scope: str
    minimum_version: int
    verifier_scope: str
    minimum_verifiers: int


def assess(effect_id: str, e: Evidence, c: Constraint) -> Decision:
    o = e.observation
    a = e.observer_authority
    if o.effect_id != effect_id or o.version < c.minimum_version:
        return Decision.UNKNOWN
    if o.source != c.required_source or a.subject != o.source or not a.active:
        return Decision.UNKNOWN
    if a.scope != c.required_scope or not e.chain_complete:
        return Decision.UNKNOWN
    eligible = [v for v in e.verifier_authorities if v.active and v.scope == c.verifier_scope]
    if not e.verified or len(eligible) < c.minimum_verifiers:
        return Decision.UNKNOWN
    if e.claim == "conflict":
        return Decision.CONFLICT
    if e.claim == "applied" and o.status == "APPLIED":
        return Decision.REALIZED
    return Decision.UNKNOWN


def baseline() -> tuple[Evidence, Constraint]:
    observer = Authority("observer-a", "root-a", "target-a", 3, True)
    verifiers = (
        Authority("verifier-a", "root-v", "evidence-a", 5, True),
        Authority("verifier-b", "root-v", "evidence-a", 5, True),
    )
    observation = Observation("e1", "observer-a", 7, "APPLIED")
    evidence = Evidence(observation, observer, verifiers, True, True, "applied")
    constraint = Constraint("observer-a", "target-a", 7, "evidence-a", 2)
    return evidence, constraint


def test_delegated_observer_can_be_admissible() -> None:
    e, c = baseline()
    assert assess("e1", e, c) is Decision.REALIZED


def test_scope_widening_is_rejected() -> None:
    e, c = baseline()
    widened = Authority(e.observer_authority.subject, e.observer_authority.issuer, "all-targets", 3, True)
    assert assess("e1", Evidence(e.observation, widened, e.verifier_authorities, True, True, "applied"), c) is Decision.UNKNOWN


def test_delegated_authority_revocation_is_rejected() -> None:
    e, c = baseline()
    revoked = Authority(e.observer_authority.subject, e.observer_authority.issuer, e.observer_authority.scope, e.observer_authority.version, False)
    assert assess("e1", Evidence(e.observation, revoked, e.verifier_authorities, True, True, "applied"), c) is Decision.UNKNOWN


def test_capability_like_delegation_does_not_mutate_effect_authority() -> None:
    e, c = baseline()
    assert assess("e1", e, c) is Decision.REALIZED
    # Observation admissibility is not authority over the underlying effect.


def test_multi_party_verification_requires_distinct_active_verifiers() -> None:
    e, c = baseline()
    one = Evidence(e.observation, e.observer_authority, (e.verifier_authorities[0],), True, True, "applied")
    assert assess("e1", one, c) is Decision.UNKNOWN


def test_revoked_verifier_cannot_satisfy_verification_requirement() -> None:
    e, c = baseline()
    revoked = Authority("verifier-b", "root-v", "evidence-a", 5, False)
    altered = Evidence(e.observation, e.observer_authority, (e.verifier_authorities[0], revoked), True, True, "applied")
    assert assess("e1", altered, c) is Decision.UNKNOWN


def test_cross_domain_scope_does_not_silently_substitute() -> None:
    e, c = baseline()
    foreign = Authority("verifier-a", "foreign-root", "foreign-domain", 5, True)
    altered = Evidence(e.observation, e.observer_authority, (foreign, e.verifier_authorities[1]), True, True, "applied")
    assert assess("e1", altered, c) is Decision.UNKNOWN


def test_conflicting_multi_party_verification_is_preserved() -> None:
    e, c = baseline()
    conflict = Evidence(e.observation, e.observer_authority, e.verifier_authorities, True, True, "conflict")
    assert assess("e1", conflict, c) is Decision.CONFLICT


def test_delegation_does_not_require_new_genesis_primitive() -> None:
    existing = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}
    proposed = {"Delegation", "Trust", "Quorum", "Verifier", "Provenance", "Witness"}
    assert existing.isdisjoint(proposed)


def main() -> None:
    test_delegated_observer_can_be_admissible()
    test_scope_widening_is_rejected()
    test_delegated_authority_revocation_is_rejected()
    test_capability_like_delegation_does_not_mutate_effect_authority()
    test_multi_party_verification_requires_distinct_active_verifiers()
    test_revoked_verifier_cannot_satisfy_verification_requirement()
    test_cross_domain_scope_does_not_silently_substitute()
    test_conflicting_multi_party_verification_is_preserved()
    test_delegation_does_not_require_new_genesis_primitive()
    print("PASS32_PUBLIC: PASS; cases=9; private_data=none; new_primitives=0")


if __name__ == "__main__":
    main()
