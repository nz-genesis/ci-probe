# External Participant Runbook v1

**Status:** `ACTIVE PUBLIC EXECUTION CONTRACT / IR-V2 COMPATIBLE`

## Purpose

This runbook defines how an independently controlled participant can execute the active frozen IR-V2 challenge without receiving private target context.

The participant is not asked to agree with any target hypothesis. The participant is asked to produce an independently generated raw result and a provenance record sufficient for later independence adjudication.

## Independence boundary

The participant MUST control the execution environment and SHOULD disclose, at the granularity appropriate to the review:

- participant identity or stable pseudonymous identifier;
- model/provider and declared version identifier;
- runtime and version;
- solver artifact digest;
- configuration digest;
- prior exposure to private research or target hypotheses;
- relationship to the operator/coordinator;
- execution timestamps.

The participant MUST NOT receive private research, unpublished expected conclusions, private prompts, private reduction maps, or adjudication context outside the frozen public challenge.

## Exact active challenge

Use the active IR-V2 challenge from `challenge-v2.json` and verify the SHA-256 of the exact bytes before execution.

The published challenge content hash is recorded in `ACTIVE_MANIFEST.md` and `INDEPENDENT_REPLICATION_CALL.md`. The participant must still recompute the digest from the exact challenge bytes actually received; a Git blob SHA-1 or commit SHA is not a substitute for the content SHA-256.

## Execution procedure

1. Obtain the exact frozen IR-V2 challenge snapshot.
2. Compute its SHA-256 from the received bytes and compare it with the supplied manifest/call value.
3. Freeze the challenge revision/hash in the run record.
4. Work only from the challenge and its public contract until the raw reconstruction is complete and frozen.
5. Independently derive the semantic basis/factorization, assumptions, coverage mapping, deletion/reduction analysis, counterexamples and unresolved cases.
6. Freeze the exact raw result before receiving or seeking any target interpretation.
7. Compute the raw-result SHA-256.
8. Create the cryptographic commitment required by the active replication protocol.
9. Preserve the exact raw bytes, nonce and provenance needed for the agreed reveal.
10. Run the public structural verifier against the exact frozen challenge.
11. Reveal only after the agreed commitment window.
12. Submit the raw result, commitment/reveal evidence, verifier output and provenance through the agreed channel.

## Blindness rule

The participant MUST NOT inspect private Genesis interpretations or target hypotheses before freezing the raw result. If contamination occurs before freeze, report it explicitly and classify the run as contaminated rather than silently continuing.

## No independence inflation

The participant MUST NOT claim material independence merely because the run uses a different process, machine, model, account, or repository. Material external independence requires independently controlled execution plus corroborating provenance under the private research review gate.

## Reproduction

A second independent participant MAY repeat the exact frozen challenge when practical. Agreement is useful corroboration but does not prove correctness. Disagreement is valid evidence and must be preserved for adjudication.

## Required public evidence package

Where publication is appropriate, preserve at least:

- challenge revision/identifier;
- challenge SHA-256 computed from exact bytes;
- raw-result SHA-256;
- commitment/reveal evidence;
- execution environment and model/runtime provenance at the declared granularity;
- candidate-visibility and contamination status;
- verifier result;
- deviations or failures;
- adversarial review status where performed.

Do not publish credentials, private nonces before reveal, API keys, private prompts, hidden system instructions, or sensitive participant data.

## Coordinator rule

The coordinator MUST freeze and preserve the participant's raw result before providing any private target interpretation or substantive adjudication context. Failed, contaminated, contradictory and ambiguous runs are retained rather than selectively discarded.

## Acceptance states

- `RAW_BLIND_RUN` — raw result frozen; material independence not yet established.
- `ATTESTED_EXECUTION` — provenance/integrity contract passed.
- `MATERIAL_EXTERNAL_INDEPENDENCE` — required independent-control criteria are corroborated by review.
- `CONTAMINATED` — blindness boundary was breached before raw freeze.
- `UNKNOWN` — available evidence is insufficient for a stronger state.

## Historical lineage

This file supersedes the earlier BIR-1-specific wording while retaining filename lineage. It is the active participant runbook for the IR-V2 campaign. Future substantive changes require a new runbook version rather than silently changing this contract after a committed run.

This runbook defines a procedure. It does not constitute evidence that any participant has executed it.
