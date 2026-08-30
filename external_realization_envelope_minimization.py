"""Clean-room minimization experiment for an external realization envelope.

Question: what is the smallest public envelope that prevents semantically relevant
private mutations from becoming indistinguishable at the realization boundary?

This is generic only. It does not encode Genesis-specific ontology, credentials,
private endpoints, datasets, or canonical decisions.
"""

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class PublicEnvelope:
    request_id: str
    operation: str
    key: str
    value: str
    constraint: str
    admission: str
    provenance_commitment: str


PUBLIC_REQUEST_FIELDS = ("request_id", "operation", "key", "value", "constraint")
SEMANTIC_FIELDS = ("authority", "resource_version", "temporal_state", "verification")


def commitment(request_id: str, field: str, value: str) -> str:
    return sha256(f"{request_id}|{field}|{value}".encode("utf-8")).hexdigest()


def private_semantic_contract(**overrides: str) -> dict[str, str]:
    contract = {
        "request_id": "envelope-001",
        "operation": "set",
        "key": "fixture",
        "value": "v1",
        "constraint": "deterministic",
        "authority": "delegated",
        "resource_version": "v1",
        "temporal_state": "valid",
        "verification": "exact-value",
    }
    contract.update(overrides)
    return contract


def private_admission(contract: dict[str, str]) -> str:
    """Private-side authority/validity decision; never exported as its inputs."""
    if contract["authority"] == "revoked":
        return "deny"
    if contract["resource_version"] != "v1":
        return "deny"
    if contract["temporal_state"] != "valid":
        return "deny"
    return "allow"


def build_envelope(contract: dict[str, str]) -> PublicEnvelope:
    commitments = "|".join(
        commitment(contract["request_id"], field, contract[field]) for field in SEMANTIC_FIELDS
    )
    return PublicEnvelope(
        *(contract[field] for field in PUBLIC_REQUEST_FIELDS),
        admission=private_admission(contract),
        provenance_commitment=sha256(commitments.encode("utf-8")).hexdigest(),
    )


def realize(envelope: PublicEnvelope) -> dict[str, str]:
    if envelope.admission == "deny":
        return {
            "request_id": envelope.request_id,
            "outcome": "not-applied",
            "observed_value": "<absent>",
            "provenance_commitment": envelope.provenance_commitment,
        }
    return {
        "request_id": envelope.request_id,
        "outcome": "applied",
        "observed_value": envelope.value,
        "provenance_commitment": envelope.provenance_commitment,
    }


def run_minimization() -> dict[str, bool]:
    baseline = private_semantic_contract()
    baseline_envelope = build_envelope(baseline)
    baseline_result = realize(baseline_envelope)

    # Each mutation changes a semantically relevant private field. The private
    # admission decision must therefore remain observable at the boundary even
    # though the underlying value stays private.
    mutations = {
        "authority": "revoked",
        "resource_version": "v2",
        "temporal_state": "expired",
    }

    results: dict[str, bool] = {}
    for field, value in mutations.items():
        mutated = private_semantic_contract(**{field: value})
        envelope = build_envelope(mutated)
        result = realize(envelope)
        results[field] = (
            envelope.provenance_commitment != baseline_envelope.provenance_commitment
            and result["outcome"] != baseline_result["outcome"]
        )

    # Verification is deliberately kept private in this envelope: it is tested
    # as post-execution private verification, not exported as a public predicate.
    verification_mutation = private_semantic_contract(verification="different-value-rule")
    verification_envelope = build_envelope(verification_mutation)
    results["verification_private"] = (
        verification_envelope.provenance_commitment != baseline_envelope.provenance_commitment
        and verification_envelope.admission == baseline_envelope.admission
    )

    assert all(results.values())
    return results


if __name__ == "__main__":
    results = run_minimization()
    print("external realization envelope minimization: PASS")
    for field, preserved in results.items():
        print(f"mutation={field} semantic_distinction_preserved={preserved}")
