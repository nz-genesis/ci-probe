# External Execution Packet v1

**Status:** `ACTIVE PUBLIC CLEAN-ROOM EXECUTION CONTRACT / IR-V2 COMPATIBLE`

## Purpose

This packet is the public material required for an external participant to execute the active independent-reconstruction challenge without receiving private target context.

The participant is not asked to agree with any target hypothesis. The participant is asked to produce an independently generated raw result and provenance sufficient for later independence adjudication.

## Active frozen challenge

Challenge: `IR-V2`

Challenge file: `independent-replication/challenge-v2.json`

Challenge SHA-256 (exact file bytes):
`03b25456a1ad0b40272daa1ca633910855433cfdce6ece8d0cf9e3352cd7ef1b`

The participant MUST recompute this digest from the exact challenge bytes actually received. A Git commit SHA or Git blob SHA-1 is not a substitute.

The participant SHOULD record the exact repository revision from which the challenge bytes were obtained.

## Blindness contract

Before freezing the raw result, the participant MUST NOT:

- inspect private Genesis repositories or private research;
- inspect a Genesis candidate basis or target hypothesis;
- receive private adjudication or comparison results;
- receive private prompts or unpublished authority material;
- ask the operator to interpret the challenge beyond this public contract.

If prior exposure exists, declare it. If contamination occurs before raw-result freeze, classify the run as `CONTAMINATED` rather than silently continuing.

## Required execution

1. Obtain the exact frozen IR-V2 challenge snapshot.
2. Verify the exact challenge SHA-256.
3. Read the challenge and this public contract only, plus ordinary documentation needed to operate the participant's own runtime.
4. Independently choose and control the model/provider/runtime/solver/configuration.
5. Produce the raw reconstruction and required supporting artifacts.
6. Freeze the raw result before target comparison or interpretation.
7. Compute SHA-256 over the exact frozen raw-result bytes.
8. Create the commitment required by the active replication protocol.
9. Preserve the exact raw bytes, nonce and provenance needed for reveal.
10. Run the public structural verifier against the exact frozen challenge.
11. Reveal only after the agreed commitment window.
12. Submit raw result, commitment/reveal evidence, verifier output and provenance through the agreed channel.

## Required submission contract

The raw submission MUST include at least:

- independently derived basis/factorization;
- case-by-case mapping to the frozen challenge;
- removal/reduction analysis;
- structured counterexamples;
- uncertainty and limitations;
- provenance;
- candidate-visibility statement;
- exact `challenge_sha256`;
- timestamp/environment data needed for reproduction.

## Independence rule

A participant MUST NOT claim material independence merely because a different process, machine, model, account, repository or API key was used.

Material external independence requires independently controlled execution plus corroborating provenance and adversarial review. Self-attestation alone is not sufficient.

## Transfer sequence

```text
participant
    -> commitment + provenance
    -> raw result frozen
    -> reveal
    -> public structural verification
    -> adversarial review
    -> private interpretation/adjudication LAST
```

Private interpretation MUST NOT be supplied before raw-result freeze.

## Public verification boundary

The public verifier may establish schema validity, challenge binding, hashes, deterministic structural checks and executable consistency where applicable.

It does not establish semantic correctness, global minimality, universality, uniqueness or agreement with a private hypothesis.

## Security boundary

Never publish credentials, access tokens, private nonces before reveal, private prompts, hidden system instructions, private research or confidential participant data.

## Historical lineage

This file retains the `v1` filename because it is a versioned public execution packet lineage. Earlier BIR-1A wording has been generalized to the active IR-V2 challenge without changing the frozen challenge itself.

Future substantive changes require a new packet version rather than silently changing this contract after a participant has committed to it.

## Non-claim

This packet defines a procedure. It is not evidence that an external participant has executed the challenge.
