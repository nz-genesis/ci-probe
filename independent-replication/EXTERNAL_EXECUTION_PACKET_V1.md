# BIR-1A External Execution Packet v1

Status: `PUBLIC CLEAN-ROOM EXECUTION CONTRACT — NOT EVIDENCE`

## Purpose

This packet is the minimum public material required for an external participant to execute the active independent reconstruction challenge without receiving Genesis private research, target hypotheses, adjudication, or candidate basis.

This packet deliberately does **not** contain an answer, target ontology, Genesis reduction map, private research, or scoring rubric for agreement with Genesis.

## Active frozen challenge

Challenge: `IR-V2`

Challenge file: `independent-replication/challenge-v2.json`

Challenge SHA-256 (exact file bytes):
`03b25456a1ad0b40272daa1ca633910855433cfdce6ece8d0cf9e3352cd7ef1b`

The participant MUST verify this SHA-256 before execution. A Git commit SHA or Git blob SHA-1 is not a substitute.

The participant SHOULD record the exact repository commit/revision from which the challenge bytes were obtained.

## Blindness contract

Before freezing the raw result, the participant MUST NOT:

- inspect Genesis private repositories or private research;
- inspect a Genesis candidate basis or target hypothesis;
- receive Genesis adjudication or comparison results;
- receive private prompts or unpublished authority material;
- ask the Genesis operator to interpret the challenge for them beyond this public contract.

If prior exposure exists, declare it. If contamination occurs after challenge receipt and before raw-result freeze, classify the run as `CONTAMINATED` rather than silently continuing.

## Required execution

1. Obtain `challenge-v2.json` from the public repository.
2. Verify the exact challenge SHA-256 above.
3. Read the challenge and this packet only, plus ordinary documentation required to operate the participant's own runtime.
4. Independently choose and control the model/provider/runtime/solver/configuration.
5. Produce the raw reconstruction.
6. Freeze the raw result before discussing its interpretation with Genesis.
7. Compute SHA-256 over the exact frozen raw-result bytes.
8. Create a commitment according to the applicable BIR-1 protocol.
9. Create `execution_attestation.json` using `execution_attestation_v1.schema.json`.
10. Preserve sufficient provenance to reproduce or audit the execution without publishing secrets.

## Required submission fields

The attestation MUST conform to:

`independent-replication/execution_attestation_v1.schema.json`

At minimum, the participant declares:

- participant identifier/type;
- challenge identifier and challenge SHA-256;
- prompt-contract SHA-256;
- model family and declared model/provider identifier;
- runtime and version;
- solver artifact digest;
- configuration digest;
- execution start/end timestamps;
- raw-result SHA-256;
- commitment SHA-256;
- prior Genesis exposure;
- relationship to Genesis operator;
- epistemic status.

## Independence rule

A participant MUST NOT claim L4 merely because a different process, machine, model, account, repository, or API key was used.

Material external independence requires independently controlled execution plus corroborating provenance and adversarial review.

Self-attestation is evidence about the participant's declaration; it is not by itself proof of independence.

## Transfer sequence

The coordinator MUST accept the raw result in a way that preserves the blind boundary:

```text
participant
    -> commitment + attestation
    -> raw result held/frozen
    -> reveal
    -> public structural verification
    -> adversarial review
    -> Genesis interpretation/adjudication LAST
```

Genesis interpretation MUST NOT be supplied before the participant's raw result is frozen.

## Public verification

After reveal, the public verifier SHOULD establish at least:

- challenge SHA-256 matches the frozen challenge bytes;
- attestation schema validates;
- raw-result SHA-256 matches exact revealed bytes;
- commitment/reveal verifies;
- provenance fields are internally consistent;
- declared independence level does not exceed the evidence available.

The verifier does not determine semantic correctness and does not prove that the challenge is complete.

## Adversarial review

The reviewer MUST use `BIR-1A_REVIEW_CHECKLIST.md` and explicitly test:

- context contamination;
- hidden operator control;
- provenance weakness;
- omitted distinctions;
- counterexamples;
- minimality claims;
- completeness assumptions;
- disagreement with Genesis as a potentially informative result.

Claims must be classified as `OBSERVED`, `DERIVED`, `HYPOTHESIS`, `UNKNOWN`, or `CONTRADICTED` where applicable.

## Security boundary

Never publish:

- API keys;
- access tokens;
- private nonces before the agreed reveal point;
- private Genesis source;
- private prompts;
- confidential participant information;
- unpublished credentials or datasets.

## Acceptance states

`RAW_BLIND_RUN` -> raw result frozen.

`ATTESTED_EXECUTION` -> attestation/provenance checks pass.

`MATERIAL_EXTERNAL_INDEPENDENCE` -> L4 evidence survives adversarial review.

`CONTAMINATED` -> blindness boundary breached.

`UNKNOWN` -> evidence insufficient for a stronger claim.

## Important non-claim

Publication of this packet, a participant declaration, a successful validator run, or agreement with a Genesis hypothesis does **not** by itself establish correctness or independence.

This file is an execution contract, not evidence that an external participant has executed the challenge.
