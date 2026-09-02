# BIR-1A External Execution Submission Template v1

Status: `TEMPLATE — NOT EVIDENCE`

Use this template after the raw result has been frozen. Do not put secrets in the submission.

## Participant declaration

- `participant_id`:
- `participant_type`: `external` / `affiliated` / `unknown`
- `genesis_operator_relationship`: `external` / `affiliated` / `unknown`
- `prior_genesis_exposure`: `yes` / `no` / `unknown`

## Challenge provenance

- `challenge_id`: `IR-V2`
- `challenge_repository_revision`:
- `challenge_sha256`: `03b25456a1ad0b40272daa1ca633910855433cfdce6ece8d0cf9e3352cd7ef1b`
- `prompt_contract_sha256`:

## Execution provenance

- `model_family`:
- `model_version_or_provider_declared_id`:
- `runtime_name`:
- `runtime_version`:
- `solver_artifact_digest`:
- `configuration_digest`:
- `execution_started_at`:
- `execution_finished_at`:

## Result integrity

- `raw_result_sha256`:
- `commitment_sha256`:
- `epistemic_status`: `RAW_BLIND_RUN` / `ATTESTED_EXECUTION` / `UNKNOWN`
- `independence_level`: `L1` / `L2` / `L3` / `L4`

## Raw result

Attach or publish the exact frozen raw result bytes according to the agreed transfer channel. Do not rewrite, summarize, or clean the raw result before hashing.

## Deviations / contamination

State any deviation from the packet or any exposure to Genesis material before raw-result freeze. If contamination occurred, use acceptance state `CONTAMINATED` and do not claim L4.

## Participant notes

Record uncertainty, challenge criticism, missing obligations, counterexamples, and alternative interpretations. These are valid research outputs even when they disagree with Genesis.
