# BIR-1A External Execution Audit Packet v1

Status: `HANDOFF / AUDIT RECORD TEMPLATE — NOT EVIDENCE`

## Purpose

This packet accompanies a raw result received from an independently controlled executor. It is completed by the coordinator/reviewer **after** the executor has frozen the raw result and commitment.

## Frozen inputs

- Challenge ID: `IR-V2`
- Challenge SHA-256: `03b25456a1ad0b40272daa1ca633910855433cfdce6ece8d0cf9e3352cd7ef1b`
- Challenge revision: `<record exact revision>`
- Prompt-contract SHA-256: `<record exact digest>`
- Raw-result SHA-256: `<record exact digest>`
- Commitment SHA-256: `<record exact digest>`

## Independence review

The reviewer must classify each item independently:

| Claim | Status |
|---|---|
| Participant controlled its execution environment | `OBSERVED / ATTESTED / UNKNOWN` |
| Participant had no Genesis private context before freeze | `OBSERVED / ATTESTED / UNKNOWN / CONTAMINATED` |
| Participant had no target hypothesis before freeze | `OBSERVED / ATTESTED / UNKNOWN / CONTAMINATED` |
| Model/provider/runtime provenance is sufficient | `OBSERVED / ATTESTED / UNKNOWN` |
| Operator relationship is external | `OBSERVED / ATTESTED / UNKNOWN` |
| Prior Genesis exposure is absent | `OBSERVED / ATTESTED / UNKNOWN` |
| L4 independence is warranted | `CONFIRMED / NOT_CONFIRMED / UNKNOWN` |

Self-attestation must never be upgraded to independent observation without additional corroboration.

## Integrity review

- [ ] Challenge bytes match declared SHA-256.
- [ ] Raw bytes match declared SHA-256.
- [ ] Commitment/reveal verifies.
- [ ] Attestation validates against schema V1.
- [ ] No secret material was published.
- [ ] No raw result was altered after freeze.

## Semantic review boundary

Do not compare the result with Genesis candidate semantics until the integrity and independence review above is frozen.

After that boundary, record:

- agreement;
- disagreement;
- novel distinctions;
- challenge criticism;
- strongest counterexamples;
- minimality/completeness arguments;
- unresolved questions.

Do not convert any of these into canonical Genesis decisions automatically.

## Acceptance state

Use exactly one primary state:

- `RAW_BLIND_RUN`
- `ATTESTED_EXECUTION`
- `MATERIAL_EXTERNAL_INDEPENDENCE`
- `CONTAMINATED`
- `UNKNOWN`

The acceptance state is an epistemic classification, not an implementation status.
