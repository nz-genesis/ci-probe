# External Execution Attestation v1

## Status

`PROTOCOL DRAFT — NOT EVIDENCE`

This artifact defines the minimum public attestation envelope for an independent blind replication. It does not itself establish independence or truth.

## Purpose

Separate four properties that must not be conflated:

1. process isolation;
2. context isolation;
3. execution provenance;
4. actor independence.

## Required public fields

```text
attestation_version
participant_id
participant_type
challenge_id
challenge_sha256
prompt_contract_sha256
model_family
model_version_or_provider_declared_id
runtime_name
runtime_version
solver_artifact_digest
configuration_digest
execution_started_at
execution_finished_at
raw_result_sha256
commitment_sha256
prior_genesis_exposure: yes|no|unknown
genesis_operator_relationship: external|affiliated|unknown
epistemic_status
```

## Secret boundary

Never publish credentials, private prompts, private nonces, API keys, hidden system instructions, private stderr, or other sensitive execution material. Public hashes may commit to private artifacts without revealing them.

## Verification rules

A verifier MUST independently recompute all available hashes from the submitted artifacts and MUST reject an attestation when the challenge digest differs from the frozen challenge.

The verifier MUST NOT infer actor independence merely from `participant_type=external`, a model name, a separate process, or a valid hash.

`prior_genesis_exposure=unknown` and `genesis_operator_relationship=unknown` are epistemic unknowns, not evidence of independence.

## Independence levels

| Level | Meaning | Claim permitted |
|---|---|---|
| L1 | separate process | process separation only |
| L2 | isolated Genesis context | blind-context claim, subject to audit |
| L3 | reproducible execution provenance | provenance claim |
| L4 | independently controlled actor/runtime | external-participant claim, subject to corroboration |

Material external independence requires L4 plus corroborating provenance and conflict-of-interest disclosure. No single attestation field is sufficient.

## Anti-laundering rule

A valid attestation proves provenance of an execution record. It does not prove correctness of the result, validity of Genesis semantics, or independence from undisclosed influence.

## Relationship to BIR-1

BIR-1 uses this envelope as an execution-provenance target. The raw result MUST be frozen before Genesis interpretation or adjudication. BIR-1 remains `RAW_BLIND_RUN` until an actor-independent execution has been established.

## Versioning

This document is immutable once used by an experiment. Any substantive change creates `EXECUTION_ATTESTATION_V2.md`; historical experiments retain the version under which they ran.
