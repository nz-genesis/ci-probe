"""Regression suite for L6j adversarial contract/effect verification."""
from contract_effect_verification import (
    ContractEvidence,
    EffectEvidence,
    Outcome,
    classify_effect,
    retry_decision,
)


def test_partial_effect_is_not_unknown_no_effect() -> None:
    e = EffectEvidence("op", True, True, True)
    assert classify_effect(e) is Outcome.PARTIAL_EFFECT


def test_unverified_observation_is_unknown() -> None:
    e = EffectEvidence("op", True, False, False)
    assert classify_effect(e) is Outcome.UNKNOWN


def test_valid_contract_does_not_prove_no_effect() -> None:
    c = ContractEvidence("op", "r", "v1", "valid", True)
    e = EffectEvidence("op", False, False, False)
    assert retry_decision(c, e, "v1") is Outcome.RETRY_UNSAFE


def test_stale_contract_blocks_retry() -> None:
    c = ContractEvidence("op", "r", "v1", "stale", True)
    e = EffectEvidence("op", False, False, False)
    assert retry_decision(c, e, "v1") is Outcome.RETRY_UNSAFE


def test_violated_contract_blocks_retry() -> None:
    c = ContractEvidence("op", "r", "v1", "violated", True)
    e = EffectEvidence("op", False, False, False)
    assert retry_decision(c, e, "v1") is Outcome.RETRY_UNSAFE


def test_revoked_authority_blocks_retry() -> None:
    c = ContractEvidence("op", "r", "v1", "valid", False)
    e = EffectEvidence("op", False, False, False)
    assert retry_decision(c, e, "v1") is Outcome.RETRY_UNSAFE


def test_observed_effect_blocks_retry() -> None:
    c = ContractEvidence("op", "r", "v1", "valid", True)
    e = EffectEvidence("op", True, False, True)
    assert retry_decision(c, e, "v1") is Outcome.RETRY_UNSAFE


def test_version_drift_blocks_retry() -> None:
    c = ContractEvidence("op", "r", "v1", "valid", True)
    e = EffectEvidence("op", False, False, False)
    assert retry_decision(c, e, "v2") is Outcome.RETRY_UNSAFE
