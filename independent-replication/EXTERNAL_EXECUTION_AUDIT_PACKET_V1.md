# External Execution Audit Packet v1

**Status:** `ACTIVE PUBLIC AUDIT CONTRACT / IR-V2 COMPATIBLE`

## Purpose

This packet accompanies a raw result from an independently controlled executor. It is completed by the coordinator/reviewer **after** the executor has frozen the raw result and commitment, and before substantive target interpretation is accepted.

## Frozen inputs

- Challenge ID: `IR-V2`
- Challenge SHA-256: `03b25456a1ad0b40272daa1ca633910855433cfdce6ece8d0cf9e3352cd7ef1b`
- Challenge revision: record the exact revision used
- Prompt-contract SHA-256: record the exact digest when applicable
- Raw-result SHA-256: record the exact digest
- Commitment SHA-256: record the exact digest

## Independence review

The reviewer must classify each item independently:

| Claim | Status |
|---|---|
| Participant controlled its execution environment | `OBSERVED / ATTESTED / UNKNOWN` |
| Participant had no private target context before freeze | `OBSERVED / ATTESTED / UNKNOWN / CONTAMINATED` |
| Participant had no target hypothesis before freeze | `OBSERVED / ATTESTED / UNKNOWN / CONTAMINATED` |
| Model/provider/runtime provenance is sufficient | `OBSERVED / ATTESTED / UNKNOWN` |
| Operator relationship is external | `OBSERVED / ATTESTED / UNKNOWN` |
| Prior private-research exposure is absent | `OBSERVED / ATTESTED / UNKNOWN` |
| Material external independence is warranted | `CONFIRMED / NOT_CONFIRMED / UNKNOWN` |

Self-attestation must not be upgraded to independent observation without additional corroboration.

## Integrity review

- [ ] Exact challenge bytes match declared SHA-256.
- [ ] Raw bytes match declared SHA-256.
- [ ] Commitment/reveal verifies.
- [ ] Required submission contract validates.
- [ ] No secret material was published.
- [ ] Raw result was not altered after freeze.
- [ ] Candidate visibility / contamination status is explicit.

## Semantic review boundary

Do not compare the result with any private target hypothesis until the integrity and independence review above is frozen.

After that boundary, record separately:

- agreement;
- disagreement;
- novel distinctions;
- challenge criticism;
- strongest counterexamples;
- minimality/completeness arguments;
- unresolved questions.

Do not convert any of these into canonical decisions automatically.

## Acceptance state

Use exactly one primary state:

- `RAW_BLIND_RUN`
- `ATTESTED_EXECUTION`
- `MATERIAL_EXTERNAL_INDEPENDENCE`
- `CONTAMINATED`
- `UNKNOWN`

The acceptance state is an epistemic classification, not an implementation status.

## Historical lineage

This file retains the `v1` filename as a versioned public audit-packet lineage. Earlier BIR-1A-specific wording has been generalized to the active IR-V2 campaign without changing the frozen challenge.

Future substantive changes require a new packet version rather than silently changing this contract after a participant has committed to it.
