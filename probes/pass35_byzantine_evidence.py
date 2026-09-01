"""Pass 35 public-safe Byzantine evidence/verifier probe.

Synthetic only. This version deliberately keeps source/verifier admissibility
outside Evidence: they are transition-specific constraints, not evidence
claims. The test asks whether compromise can be handled with the existing
candidate basis rather than a Trust/Verifier/Provenance/Witness primitive.
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


@dataclass(frozen=True)
class Constraint:
    admissible_observers: frozenset[str]
    verifier_admissible: bool


def authority_matches(a: Authority, t: Transition) -> bool:
    return (
        a.subject == t.subject
        and a.issuer == t.issuer
        and a.scope == t.scope
        and a.version == t.authority_version
        and a.active
    )


def supports(e: Evidence, t: Transition, c: Constraint) -> bool:
    return (
        e.complete
        and c.verifier_admissible
        and e.observation.observer in c.admissible_observers
        and e.observation.effect_id == t.effect_id
        and e.observation.version >= t.observation_version
        and e.observation.status == "APPLIED"
        and e.claim == "applied"
        and authority_matches(e.authority, t)
    )


def contradicts(e: Evidence, t: Transition, c: Constraint) -> bool:
    return (
        e.complete
        and c.verifier_admissible
        and e.observation.observer in c.admissible_observers
        and e.observation.effect_id == t.effect_id
        and e.observation.version >= t.observation_version
        and e.claim in {"revoked", "conflict"}
        and authority_matches(e.authority, t)
    )


def assess(t: Transition, evidence: tuple[Evidence, ...], c: Constraint) -> Decision:
    good = tuple(e for e in evidence if supports(e, t, c))
    bad = tuple(e for e in evidence if contradicts(e, t, c))
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


def base() -> tuple[Transition, Authority, Evidence, Constraint]:
    a = Authority("subject-a", "root-a", "target-a", 7, True)
    t = Transition("effect-35", "subject-a", "root-a", "target-a", 7, 7)
    o = Observation("effect-35", "observer-a", 7, "APPLIED")
    e = Evidence(o, a, "applied", True)
    c = Constraint(frozenset({"observer-a"}), True)
    return t, a, e, c


def test_valid_evidence_allows() -> None:
    t, _, e, c = base()
    assert assess(t, (e,), c) is Decision.ALLOW


def test_compromised_observer_cannot_supply_authoritative_evidence() -> None:
    t, _, e, _ = base()
    c = Constraint(frozenset(), True)
    assert assess(t, (e,), c) is Decision.UNKNOWN


def test_compromised_verifier_cannot_supply_authoritative_evidence() -> None:
    t, _, e, _ = base()
    c = Constraint(frozenset({"observer-a"}), False)
    assert assess(t, (e,), c) is Decision.UNKNOWN


def test_legitimate_authority_does_not_make_false_observation_true() -> None:
    t, _, e, c = base()
    false_observation = Evidence(
        Observation("effect-35", "observer-a", 7, "FAILED"),
        e.authority,
        "applied",
        True,
    )
    assert assess(t, (false_observation,), c) is Decision.UNKNOWN


def test_valid_observation_with_wrong_authority_is_unknown() -> None:
    t, _, e, c = base()
    wrong = Authority("subject-a", "foreign-root", "target-a", 7, True)
    forged = Evidence(e.observation, wrong, "applied", True)
    assert assess(t, (forged,), c) is Decision.UNKNOWN


def test_legitimate_observer_with_forged_claim_is_unknown() -> None:
    t, _, e, c = base()
    forged = Evidence(e.observation, e.authority, "applied", True)
    c = Constraint(frozenset(), True)
    assert assess(t, (forged,), c) is Decision.UNKNOWN


def test_verifier_cannot_create_authority() -> None:
    t, a, e, c = base()
    assert e.authority.subject == t.subject
    assert e.observation.observer != t.subject
    assert assess(t, (e,), c) is Decision.ALLOW


def test_conflicting_admissible_evidence_is_not_silently_resolved() -> None:
    t, _, e, c = base()
    contradictory = Evidence(
        Observation("effect-35", "observer-b", 7, "APPLIED"),
        e.authority,
        "conflict",
        True,
    )
    c = Constraint(frozenset({"observer-a", "observer-b"}), True)
    assert assess(t, (e, contradictory), c) is Decision.CONFLICT


def test_compromised_source_is_ignored_when_independent_valid_source_exists() -> None:
    t, _, e, _ = base()
    compromised = Evidence(e.observation, e.authority, "applied", True)
    valid = Evidence(
        Observation("effect-35", "observer-b", 7, "APPLIED"),
        e.authority,
        "applied",
        True,
    )
    c = Constraint(frozenset({"observer-b"}), True)
    assert assess(t, (compromised, valid), c) is Decision.ALLOW


def test_incomplete_evidence_is_not_execution_proof() -> None:
    t, _, e, c = base()
    incomplete = Evidence(e.observation, e.authority, "applied", False)
    assert assess(t, (incomplete,), c) is Decision.UNKNOWN


def test_stale_observation_cannot_verify_newer_effect() -> None:
    t, _, e, c = base()
    stale = Evidence(Observation("effect-35", "observer-a", 6, "APPLIED"), e.authority, "applied", True)
    assert assess(t, (stale,), c) is Decision.UNKNOWN


def test_unknown_is_not_retry_permission() -> None:
    t, _, e, _ = base()
    c = Constraint(frozenset(), True)
    assert assess(t, (e,), c) is Decision.UNKNOWN
    assert assess(t, (e,), c) is Decision.UNKNOWN


def test_capability_is_not_authority() -> None:
    t, _, e, _ = base()
    c = Constraint(frozenset(), True)
    assert e.observation.observer != e.authority.subject
    assert assess(t, (e,), c) is Decision.UNKNOWN


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
