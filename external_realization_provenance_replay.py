"""Bounded clean-room test for provenance binding, replay, and substitution.

This is generic security-boundary evidence only. It does not encode Genesis
ontology and does not claim that a cryptographic mechanism is a Genesis
primitive. The verifier-side secret/state are represented explicitly so the
attack model is not confused with a public digest alone.
"""
from dataclasses import dataclass
from hashlib import sha256
import hmac


VERIFIER_KEY = b"generic-clean-room-verifier-key"


@dataclass(frozen=True)
class PrivateContract:
    operation: int
    resource_version: int
    authority_min: int
    authority_max: int
    expected_value: int


@dataclass(frozen=True)
class Envelope:
    contract_commitment: str
    request_id: str
    envelope_nonce: str
    operation: int
    resource_version: int
    observed_epoch: int
    expected_value: int


@dataclass(frozen=True)
class Receipt:
    envelope_digest: str
    realizer_id: str
    effect_digest: str
    nonce: str
    tag: str


def stable_digest(*values: object) -> str:
    payload = "|".join(str(v) for v in values)
    return sha256(payload.encode()).hexdigest()


def contract_commitment(contract: PrivateContract) -> str:
    return stable_digest(
        contract.operation,
        contract.resource_version,
        contract.authority_min,
        contract.authority_max,
        contract.expected_value,
    )


def envelope_digest(envelope: Envelope) -> str:
    return stable_digest(
        envelope.contract_commitment,
        envelope.request_id,
        envelope.envelope_nonce,
        envelope.operation,
        envelope.resource_version,
        envelope.observed_epoch,
        envelope.expected_value,
    )


def receipt_tag(envelope: Envelope, realizer_id: str, effect_digest: str) -> str:
    material = "|".join(
        [envelope_digest(envelope), realizer_id, effect_digest, envelope.envelope_nonce]
    )
    return hmac.new(VERIFIER_KEY, material.encode(), "sha256").hexdigest()


def issue_receipt(envelope: Envelope, realizer_id: str, effect_digest: str) -> Receipt:
    return Receipt(
        envelope_digest=envelope_digest(envelope),
        realizer_id=realizer_id,
        effect_digest=effect_digest,
        nonce=envelope.envelope_nonce,
        tag=receipt_tag(envelope, realizer_id, effect_digest),
    )


def verify_receipt(
    contract: PrivateContract,
    envelope: Envelope,
    receipt: Receipt,
    consumed_nonces: set[str],
) -> tuple[bool, str]:
    if envelope.contract_commitment != contract_commitment(contract):
        return False, "contract-substitution"
    if envelope_digest(envelope) != receipt.envelope_digest:
        return False, "envelope-substitution"
    if receipt.nonce != envelope.envelope_nonce:
        return False, "nonce-substitution"
    if receipt.nonce in consumed_nonces:
        return False, "replay"
    expected_tag = receipt_tag(envelope, receipt.realizer_id, receipt.effect_digest)
    if not hmac.compare_digest(expected_tag, receipt.tag):
        return False, "forged-receipt"
    consumed_nonces.add(receipt.nonce)
    return True, "accepted"


def base() -> tuple[PrivateContract, Envelope, Receipt]:
    contract = PrivateContract(1, 7, 10, 20, 42)
    envelope = Envelope(
        contract_commitment=contract_commitment(contract),
        request_id="opaque-request",
        envelope_nonce="opaque-nonce-01",
        operation=1,
        resource_version=7,
        observed_epoch=15,
        expected_value=42,
    )
    effect = stable_digest("effect", 42)
    return contract, envelope, issue_receipt(envelope, "opaque-realizer", effect)


def attack_suite() -> dict[str, bool]:
    contract, envelope, receipt = base()
    results: dict[str, bool] = {}

    state: set[str] = set()
    accepted, reason = verify_receipt(contract, envelope, receipt, state)
    results["baseline_accept"] = accepted and reason == "accepted"

    accepted, reason = verify_receipt(contract, envelope, receipt, state)
    results["replay_rejected"] = (not accepted) and reason == "replay"

    substituted = Envelope(
        **{**envelope.__dict__, "resource_version": 8}
    )
    accepted, reason = verify_receipt(contract, substituted, receipt, set())
    results["envelope_substitution_rejected"] = (not accepted) and reason == "envelope-substitution"

    contract_substituted = PrivateContract(1, 8, 10, 20, 42)
    accepted, reason = verify_receipt(contract_substituted, envelope, receipt, set())
    results["contract_substitution_rejected"] = (not accepted) and reason == "contract-substitution"

    accepted, reason = verify_receipt(contract, envelope, Receipt(
        receipt.envelope_digest,
        "other-realizer",
        receipt.effect_digest,
        receipt.nonce,
        receipt.tag,
    ), set())
    results["realizer_substitution_rejected"] = not accepted

    forged = Receipt(
        receipt.envelope_digest,
        receipt.realizer_id,
        stable_digest("different-effect"),
        receipt.nonce,
        receipt.tag,
    )
    accepted, reason = verify_receipt(contract, envelope, forged, set())
    results["effect_substitution_rejected"] = not accepted

    assert all(results.values()), results
    return results


if __name__ == "__main__":
    results = attack_suite()
    print("PROVENANCE BASELINE + ATTACKS: PASS")
    print("results", results)
