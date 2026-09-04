# External Execution Attestation v1

## Status

`HISTORICAL PROTOCOL DRAFT — NOT ACTIVE / NOT EVIDENCE`

This artifact records an earlier proposed attestation envelope for independent blind replication. It is retained for provenance and design genealogy. It is not the active participant contract and must not be cited as the current binding protocol.

## Purpose

The draft separated four properties that must not be conflated:

1. process isolation;
2. context isolation;
3. execution provenance;
4. actor independence.

## Historical required fields

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

## Historical verification rules

The draft required recomputation of available hashes and rejection on challenge-digest mismatch. It explicitly prohibited inferring actor independence merely from participant type, model name, process separation or valid hashes.

## Historical independence levels

| Level | Meaning | Claim permitted |
|---|---|---|
| L1 | separate process | process separation only |
| L2 | isolated private context | blind-context claim, subject to audit |
| L3 | reproducible execution provenance | provenance claim |
| L4 | independently controlled actor/runtime | external-participant claim, subject to corroboration |

These levels are retained as historical methodology only. The current active replication surface is defined by the active IR-V2 runbook, execution packet and audit requirements linked from `ACTIVE_MANIFEST.md`.

## Non-claims

This draft never established semantic correctness, material independence or Genesis canonical status. A valid attestation is not itself semantic evidence.

## Supersession

The active replication campaign uses the current documents explicitly marked `ACTIVE` in `independent-replication/ACTIVE_MANIFEST.md`. Any future attestation contract must be introduced as a new version and added to the manifest only after explicit activation.
