# IR-V3 — External Agent Task

**Status:** `ACTIVE OPERATIONAL TASK WRAPPER`
**Scope:** public `ci-probe` only
**Purpose:** provide a copy/paste-ready task for an independently controlled external agent to execute the frozen IR-V3 challenge.

This file does **not** contain or reveal the Genesis target hypothesis. It operationalizes the existing public IR-V3 protocol and runbook; it does not replace them.

## 1. Critical independence rule

The participant MUST be independently controlled from the Genesis operator for the execution to be considered for `MATERIAL_EXTERNAL_INDEPENDENCE`.

Strongest preferred topology:

```text
Genesis operator / nz-genesis
        │
        │ public frozen challenge only
        ▼
EXTERNAL PARTICIPANT
        │
        ├── own model/provider/runtime
        ├── own execution environment
        ├── own GitHub account / fork
        └── own Git history
                │
                ▼
        PR → nz-genesis/ci-probe
```

A branch inside `nz-genesis/ci-probe`, a second machine controlled by the same operator, a different persona, or a different prompt is **not** sufficient by itself.

GitHub's fork-and-pull model is preferred because a fork is a separate repository with its own branches and permissions, while still allowing a reviewable pull request to the upstream repository. The participant should retain control of the fork and must not grant maintainers permission to edit the submission branch before the evidence is frozen.

## 2. Public inputs only

The participant may use only these public artifacts until the raw result is frozen:

- `independent-replication/challenge-v3.json`
- `independent-replication/EXTERNAL_AGENT_EXECUTION_PROTOCOL_V2.md`
- `independent-replication/EXTERNAL_PARTICIPANT_RUNBOOK_V2.md`
- `independent-replication/execution_attestation_v2.schema.json`

Frozen challenge identity:

- challenge ID: `IR-V3`
- schema version: `3.0.0`
- challenge commit: `3d37e023b49a995b466954445c1672f5d7ef046d`
- challenge content SHA-256: `50f41fdc1a7d563367fb07316f2c84adc95c74a0`

**Do not use `challenge-v2.json`.**

Before raw-result freeze, do **not** request, search for, or inspect:

- `nz-genesis/genesis-lab` private research;
- the current seven-element candidate;
- BIR-1A or previous adjudication;
- private reduction maps;
- expected answer or target interpretation.

If such information is exposed before raw freeze, stop and report `CONTAMINATED`; do not present the run as a clean IR-V3 replication.

## 3. Required execution

1. Create your own fork of `nz-genesis/ci-probe`.
2. Clone your fork locally.
3. Obtain the exact frozen challenge bytes from commit `3d37e023b49a995b466954445c1672f5d7ef046d`.
4. Independently compute SHA-256 of those exact bytes and confirm `50f41fdc1a7d563367fb07316f2c84adc95c74a0`.
5. Confirm `challenge_id = IR-V3` and `schema_version = 3.0.0`.
6. Declare participant/model/provider/runtime provenance and prior Genesis exposure before semantic work.
7. Generate the semantic reconstruction using only the frozen challenge and public protocol.
8. Freeze the exact raw result locally.
9. Compute `raw_result_sha256` from the exact raw bytes.
10. Create a unique `run_id`.
11. Create the required cryptographic commitment **before any target comparison**. Recommended reproducible construction for this task:

   ```text
   commitment_sha256 = SHA256( raw_result_sha256 + "\n" + run_id )
   ```

   where the concatenation is UTF-8 encoded exactly as shown. Record the exact `run_id`, raw-result SHA-256 and commitment SHA-256.

12. **First public commit:** publish only the commitment/attestation metadata required to establish that the raw-result digest was committed before the raw result was publicly revealed. Do not include the raw result in this commit.
13. Push that commit to your own fork and preserve its commit SHA.
14. **Second public commit:** add the exact frozen raw result bytes and the reveal information needed to recompute and verify the commitment.
15. Push the second commit to your fork without rewriting the first commitment commit.
16. Open a pull request from your fork to `nz-genesis/ci-probe` and identify both commit SHAs.
17. Do not allow upstream maintainers to edit the submission branch before the evidence has been reviewed. If your GitHub workflow requires maintainer-edit permission, leave it disabled for this replication.
18. Run the public structural verifier if available and report its exact result, but do not treat that verifier as semantic proof.

## 4. Required submission contents

Place the submission under a participant-specific path such as:

```text
independent-replication/submissions/IR-V3/<participant-id>/
```

Required files:

```text
raw_result.md
execution_attestation.json
commitment_reveal.md
provenance.md
```

`raw_result.md` MUST contain:

- basis/factors;
- semantic definitions;
- mapping for every frozen case;
- observable distinctions preserved;
- deletion/removal analysis;
- explicit composition rules;
- counterexamples/failure cases;
- uncertainty/unknown handling;
- declared minimality objective;
- explicit H4/no-finite-basis treatment;
- any criticism of the challenge or omitted obligation.

`execution_attestation.json` MUST validate against `execution_attestation_v2.schema.json`.

`provenance.md` MUST state, at minimum:

- stable participant ID;
- participant type;
- model family;
- model/provider identifier;
- runtime and version;
- execution-control mechanism at a non-sensitive level;
- solver/configuration digest where applicable;
- execution start/end;
- prior Genesis exposure;
- relationship to Genesis operator;
- whether raw output was frozen before target comparison;
- contamination status;
- any unavailable field and why.

Do not publish credentials, API keys, private system prompts, private nonces or sensitive personal information.

## 5. What counts as a valid result

The participant is **not** expected to reproduce any Genesis hypothesis.

All of these are admissible:

- same normalized basis;
- smaller basis;
- different basis;
- additional irreducible distinction;
- counterexample to a finite basis;
- H4/no-finite-basis conclusion;
- criticism that the challenge is under-specified.

Agreement with Genesis is neither required nor sufficient.

## 6. Required semantic discipline

Do not smuggle removed semantics into:

- opaque identifiers;
- undeclared relation labels;
- case names;
- implementation metadata;
- evaluator-side dictionaries;
- post-hoc changes to the minimality objective.

The result must be independently intelligible from the public challenge and the participant's declared semantics.

## 7. Do not perform target comparison

The participant should stop after producing and freezing the independent result. The Genesis operator/coordinator performs any comparison only after:

```text
raw freeze
→ raw SHA verification
→ commitment verification
→ provenance review
→ material-independence adjudication
→ semantic comparison
```

A participant must not request the private target to decide how to write the result.

## 8. Failure handling

Preserve failures rather than replacing them:

- wrong challenge version → `OUT_OF_SCOPE / REJECTED`
- target leakage before raw freeze → `CONTAMINATED`
- incomplete provenance → `UNKNOWN` or provenance-incomplete
- missing/late commitment → provenance gate failure
- disagreement with target → valid scientific result, not execution failure
- inability to establish material independence → `BLOCKED / NO MATERIAL INDEPENDENCE`

The purpose is independent measurement, not confirmation.

## 9. Final handoff

The pull request description MUST state:

- participant ID;
- challenge SHA-256;
- raw-result SHA-256;
- commitment SHA-256;
- commitment commit SHA;
- reveal commit SHA;
- attestation path;
- raw-result path;
- whether any contamination occurred;
- any unavailable provenance field and why.

Do not merge the submission into `main` merely to make it look canonical. The PR/fork history is the execution witness.

## 10. Final status boundary

This task file is an execution procedure only. Completion of the task does not establish Genesis semantics by itself.

The receiving side must independently adjudicate:

```text
RAW_BLIND_RUN
→ INTEGRITY_VERIFIED
→ PROVENANCE_SUFFICIENT
→ MATERIAL_EXTERNAL_INDEPENDENCE
→ SEMANTIC_ADJUDICATION
→ RED TEAM
→ OMISSION GATE
```
