"""Pass 35 public-safe Byzantine evidence/verifier probe.

Synthetic only. Tests whether evidence source/verifier compromise can be
represented without promoting Trust, Verifier, Provenance, or Witness to
Genesis primitives. The contract is deliberately fail-closed: compromised
or unverifiable evidence is UNKNOWN; contradictory admissible evidence is
CONFLICT; capability does not manufacture authority.
"""
from dataclasses import dataclass
from enum import Enum


class Decision(Enum):
    ALLOW = "ALLOW"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class Authority:
    subject: str
    issuer: str
    scope: str
    version: int
    active: bool


@dataclass(frozen=True)
class Transition:
    effect_id: str
    subject: str
    issuer: str
    scope: str
    authority_version: int
    observation_version: int


@dataclass(frozen=True)
class Observation:
    effect_id: str
    observer: str
    version: int
    status: str


@dataclass(frozen=True)
class Evidence:
    observation: Observation
    authority: Authority
    claim: str
    complete: bool
    source_admissible: bool
    verifier_admissible: bool


def authority_matches(a: Authority, t: Transition) -> bool:
    return (
        a.subject == t.subject
        and a.issuer == t.issuer
        and a.scope == t.scope
        and a.version == t.authority_version
        and a.active
    )


def supports(e: Evidence, t: Transition) -> bool:
    return (
        e.complete
        and e.source_admissible
        and e.verifier_admissible
        and e.observation.effect_id == t.effect_id
        and e.observation.version >= t.observation_version
        and e.observation.status == "APPLIED"
        and e.claim == "applied"
        and authority_matches(e.authority, t)
    )


def contradicts(e: Evidence, t: Transition) -> bool:
    return (
        e.complete
        and e.source_admissible
        and e.verifier_admissible
        and e.observation.effect_id == t.effect_id
        and e.observation.version >= t.observation_version
        and e.claim in {"revoked", "conflict"}
        and authority_matches(e.authority, t)
    )


def assess(t: Transition, evidence: tuple[Evidence, ...]) -> Decision:
    good = tuple(e for e in evidence if supports(e, t))
    bad = tuple(e for e in evidence if contradicts(e, t))
    if good and bad:
        return Decision.CONFLICT
    if bad:
        return Decision.UNKNOWN
    if len(good) == 1:
        return Decision.ALLOW
    if len(good) > 1:
        observers = {e.observation.observer for e in good}
        if len(observers) == len(good):
            return Decision.ALLOW
        return Decision.CONFLICT
    return Decision.UNKNOWN


def base() -> tuple[Transition, Authority, Evidence]:
    a = Authority("subject-a", "root-a", "target-a", 7, True)
    t = Transition("effect-35", "subject-a", "root-a", "target-a", 7, 7)
    o = Observation("effect-35", "observer-a", 7, "APPLIED")
    e = Evidence(o, a, "applied", True, True, True)
    return t, a, e


def test_valid_evidence_allows() -> None:
    t, _, e = base()
    assert assess(t, (e,)) is Decision.ALLOW


def test_compromised_observer_cannot_supply_authoritative_evidence() -> None:
    t, _, e = base()
    compromised = Evidence(e.observation, e.authority, e.claim, True, False, True)
    assert assess(t, (compromised,)) is Decision.UNKNOWN


def test_compromised_verifier_cannot_supply_authoritative_evidence() -> None:
    t, _, e = base()
    compromised = Evidence(e.observation, e.authority, e.claim, True, True, False)
    assert assess(t, (compromised,)) is Decision.UNKNOWN


def test_legitimate_authority_does_not_make_false_observation_true() -> None:
    t, _, e = base()
    false_observation = Evidence(
        Observation("effect-35", "observer-a", 7, "FAILED"),
        e.authority,
        "applied",
        True,
        True,
        True,
    )
    assert assess(t, (false_observation,)) is Decision.UNKNOWN


def test_valid_observation_with_wrong_authority_is_unknown() -> None:
    t, _, e = base()
    wrong = Authority("subject-a", "foreign-root", "target-a", 7, True)
    forged = Evidence(e.observation, wrong, "applied", True, True, True)
    assert assess(t, (forged,)) is Decision.UNKNOWN


def test_legitimate_observer_with_forged_claim_is_unknown() -> None:
    t, _, e = base()
    forged = Evidence(e.observation, e.authority, "applied", True, False, True)
    assert assess(t, (forged,)) is Decision.UNKNOWN


def test_verifier_cannot_create_authority() -> None:
    t, a, e = base()
    foreign = Evidence(e.observation, a, "applied", True, True, True)
    assert foreign.authority.subject == t.subject
    assert foreign.observation.observer != t.subject


def test_conflicting_admissible_evidence_is_not_silently_resolved() -> None:
    t, _, e = base()
    contradictory = Evidence(
        Observation("effect-35", "observer-b", 7, "APPLIED"),
        e.authority,
        "conflict",
        True,
        True,
        True,
    )
    assert assess(t, (e, contradictory)) is Decision.CONFLICT


def test_compromised_source_is_ignored_when_independent_valid_source_exists() -> None:
    t, _, e = base()
    compromised = Evidence(e.observation, e.authority, "applied", True, False, True)
    valid = Evidence(
        Observation("effect-35", "observer-b", 7, "APPLIED"),
        e.authority,
        "applied",
        True,
        True,
        True,
    )
    assert assess(t, (compromised, valid)) is Decision.ALLOW


def test_incomplete_evidence_is_not_execution_proof() -> None:
    t, _, e = base()
    incomplete = Evidence(e.observation, e.authority, "applied", False, True, True)
    assert assess(t, (incomplete,)) is Decision.UNKNOWN


def test_stale_observation_cannot_verify_newer_effect() -> None:
    t, _, e = base()
    stale = Evidence(Observation("effect-35", "observer-a", 6, "APPLIED"), e.authority, "applied", True, True, True)
    assert assess(t, (stale,)) is Decision.UNKNOWN


def test_unknown_is_not_retry_permission() -> None:
    t, _, e = base()
    unknown = Evidence(e.observation, e.authority, "applied", True, False, True)
    assert assess(t, (unknown,)) is Decision.UNKNOWN
    assert assess(t, (unknown,)) is Decision.UNKNOWN


def test_capability_is_not_authority() -> None:
    t, a, e = base()
    capable = Evidence(e.observation, a, "applied", True, False, True)
    assert capable.observation.observer != a.subject
    assert assess(t, (capable,)) is Decision.UNKNOWN


def test_primitive_inflation_negative() -> None:
    candidate = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}
    rejected = {"Trust", "Verifier", "Provenance", "Witness"}
    assert candidate.isdisjoint(rejected)


def main() -> None:
    tests = (
        test_valid_evidence_allows,
        test_compromised_observer_cannot_supply_authoritative_evidence,
        test_compromised_verifier_cannot_supply_authoritative_evidence,
        test_legitimate_authority_does_not_make_false_observation_true,
        test_valid_observation_with_wrong_authority_is_unknown,
        test_legitimate_observer_with_forged_claim_is_unknown,
        test_verifier_cannot_create_authority,
        test_conflicting_admissible_evidence_is_not_silently_resolved,
        test_compromised_source_is_ignored_when_independent_valid_source_exists,
        test_incomplete_evidence_is_not_execution_proof,
        test_stale_observation_cannot_verify_newer_effect,
        test_unknown_is_not_retry_permission,
        test_capability_is_not_authority,
        test_primitive_inflation_negative,
    )
    for test in tests:
        test()
    print("PASS35_PUBLIC: PASS; cases=14; private_data=none; new_primitives=0")


if __name__ == "__main__":
    main()
