"""Clean-room L6j adversarial contract/effect verification probe."""
from dataclasses import dataclass
from enum import Enum


class Outcome(str, Enum):
    VERIFIED_NO_EFFECT = "verified_no_effect"
    EFFECT_OBSERVED = "effect_observed"
    PARTIAL_EFFECT = "partial_effect"
    UNKNOWN = "unknown"
    RETRY_UNSAFE = "retry_unsafe"


@dataclass(frozen=True)
class ContractEvidence:
    operation_id: str
    resource_id: str
    resource_version: str
    status: str  # valid, stale, violated, unknown
    authority_valid: bool


@dataclass(frozen=True)
class EffectEvidence:
    operation_id: str
    observed: bool
    partial: bool
    externally_verified: bool


def classify_effect(evidence: EffectEvidence) -> Outcome:
    if evidence.partial:
        return Outcome.PARTIAL_EFFECT
    if evidence.observed and evidence.externally_verified:
        return Outcome.EFFECT_OBSERVED
    if evidence.observed:
        return Outcome.UNKNOWN
    return Outcome.UNKNOWN


def retry_decision(contract: ContractEvidence, effect: EffectEvidence, current_version: str) -> Outcome:
    if classify_effect(effect) in {Outcome.EFFECT_OBSERVED, Outcome.PARTIAL_EFFECT}:
        return Outcome.RETRY_UNSAFE
    if classify_effect(effect) is Outcome.UNKNOWN:
        return Outcome.RETRY_UNSAFE
    if contract.status != "valid" or not contract.authority_valid:
        return Outcome.RETRY_UNSAFE
    if contract.resource_version != current_version:
        return Outcome.RETRY_UNSAFE
    return Outcome.RETRY_UNSAFE


def verify() -> None:
    valid = ContractEvidence("op", "r", "v1", "valid", True)
    stale = ContractEvidence("op", "r", "v1", "stale", True)
    violated = ContractEvidence("op", "r", "v1", "violated", True)
    revoked = ContractEvidence("op", "r", "v1", "valid", False)
    none = EffectEvidence("op", False, False, False)
    observed = EffectEvidence("op", True, False, True)
    partial = EffectEvidence("op", True, True, True)
    unverified_observation = EffectEvidence("op", True, False, False)

    assert classify_effect(none) is Outcome.UNKNOWN
    assert classify_effect(observed) is Outcome.EFFECT_OBSERVED
    assert classify_effect(partial) is Outcome.PARTIAL_EFFECT
    assert classify_effect(unverified_observation) is Outcome.UNKNOWN

    # The conservative result is deliberate: this pass asks whether contract
    # validity can manufacture proof of no effect. It cannot.
    assert retry_decision(valid, none, "v1") is Outcome.RETRY_UNSAFE
    assert retry_decision(stale, none, "v1") is Outcome.RETRY_UNSAFE
    assert retry_decision(violated, none, "v1") is Outcome.RETRY_UNSAFE
    assert retry_decision(revoked, none, "v1") is Outcome.RETRY_UNSAFE
    assert retry_decision(valid, observed, "v1") is Outcome.RETRY_UNSAFE
    assert retry_decision(valid, partial, "v1") is Outcome.RETRY_UNSAFE
    assert retry_decision(valid, unverified_observation, "v1") is Outcome.RETRY_UNSAFE
    assert retry_decision(valid, none, "v2") is Outcome.RETRY_UNSAFE


if __name__ == "__main__":
    verify()
    print("CONTRACT EFFECT VERIFICATION 12/12 PASS")
