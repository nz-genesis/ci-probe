# BIR-1A External Participant Runbook v1

Status: `PUBLIC EXECUTION CONTRACT — NOT EVIDENCE`

## Purpose

This runbook defines how an independently controlled participant can execute a frozen BIR-1 challenge without receiving Genesis private context.

The participant is not asked to agree with Genesis. The participant is asked to produce an independently generated raw result and provenance record.

## Independence boundary

The participant MUST control the execution environment and MUST disclose:

- participant identity or stable pseudonymous identifier;
- model/provider and declared version identifier;
- runtime and version;
- solver artifact digest;
- configuration digest;
- prior exposure to Genesis materials;
- relationship to the Genesis operator.

The participant MUST NOT receive Genesis adjudication, expected conclusions, private research corpus, or private prompts outside the frozen challenge contract.

## Execution procedure

1. Obtain the frozen challenge from the experiment coordinator.
2. Verify the supplied challenge SHA-256 before execution.
3. Verify the prompt-contract SHA-256.
4. Execute the challenge without consulting Genesis private material.
5. Freeze the raw result before discussing or interpreting it with the coordinator.
6. Compute the raw-result SHA-256.
7. Produce the commitment required by the BIR-1 protocol.
8. Produce `execution_attestation.json` using `execution_attestation_v1.schema.json`.
9. Preserve the exact solver artifact and configuration used for the run, or preserve their independently reproducible digests where publication of the artifacts is inappropriate.
10. Submit the raw result and attestation through the agreed public/private transfer channel.

## Blindness rule

The participant MUST NOT inspect Genesis interpretations before freezing the raw result. If contamination occurs, report it explicitly and classify the run as contaminated rather than silently continuing.

## No independence inflation

The participant MUST NOT claim L4 merely because the run used a different process, machine, model, account, or repository. L4 requires independently controlled execution plus corroborating provenance.

## Reproduction

A second independent participant SHOULD repeat the same frozen challenge when practical. Agreement is useful corroboration but is not proof of correctness. Disagreement is evidence requiring analysis, not automatic failure of either participant.

## Public evidence package

The public package SHOULD contain, at minimum:

- frozen challenge digest;
- prompt-contract digest;
- attestation schema version;
- raw-result digest;
- commitment/reveal evidence;
- model/runtime provenance at the declared granularity;
- independence/conflict disclosure;
- verifier result;
- adversarial review result.

Do not publish credentials, private nonces, API keys, private prompts, or sensitive participant data.

## Coordinator rule

The coordinator MUST freeze the participant's raw result before providing Genesis interpretation or adjudication context. The coordinator MUST preserve failed, contaminated, or ambiguous runs rather than selecting only favorable outcomes.

## Acceptance states

- `RAW_BLIND_RUN` — raw result frozen; independence not yet established.
- `ATTESTED_EXECUTION` — attestation schema and provenance checks pass.
- `MATERIAL_EXTERNAL_INDEPENDENCE` — L4 criteria are corroborated by the review gate.
- `CONTAMINATED` — blindness boundary was breached.
- `UNKNOWN` — evidence is insufficient for a stronger state.

This runbook defines a procedure. It does not constitute evidence that any participant has executed it.
