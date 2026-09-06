# External Participant Runbook v2

**Status:** `ACTIVE PUBLIC EXECUTION CONTRACT / IR-V3`

## Purpose

This runbook defines how an independently controlled participant can execute the frozen IR-V3 challenge without receiving private target context.

The participant is not asked to agree with any target hypothesis. The participant is asked to produce an independently generated raw result and a provenance record sufficient for later integrity and material-independence adjudication.

## Active challenge

Use the frozen IR-V3 challenge from `challenge-v3.json`.

Required challenge identity:

- `challenge_id`: `IR-V3`
- `schema_version`: `3.0.0`
- content SHA-256: `913c162ede3741ead44dca3efe3fbbf33f5de764254d6a2da88cc90cf08b05a`
- Git blob SHA-1: `50f41fdc1a7d563367fb07316f2c84adc95c74a0`
- frozen commit: `3d37e023b49a995b466954445c1672f5d7ef046d`

The participant MUST recompute the SHA-256 from the exact challenge bytes actually received. A Git blob SHA-1 or commit SHA is not a substitute for the content SHA-256. The frozen challenge's internal `sha` field is the Git blob SHA-1 and is not the protocol content SHA-256.

**Do not use `challenge-v2.json` for an IR-V3 submission.** IR-V2 remains historical evidence only.

## Independence boundary

The participant MUST control the execution environment and SHOULD disclose, at the granularity appropriate to review:

- stable participant identifier;
- participant type;
- model family and provider/version identifier;
- runtime and version;
- solver artifact digest where applicable;
- configuration digest where applicable;
- prior exposure to private Genesis research or target hypotheses;
- relationship to the Genesis operator/coordinator;
- execution-control mechanism;
- execution timestamps.

Public pseudonymity is permitted. Public anonymity alone is not evidence of material independence.

The participant MUST NOT receive private Genesis research, the current seven-element candidate, prior adjudication, BIR-1A results, private reduction maps, or expected answers before raw-result freeze.

## Required execution sequence

1. Obtain the exact frozen `challenge-v3.json` bytes.
2. Verify `challenge_id = IR-V3` and `schema_version = 3.0.0`.
3. Compute and record the challenge SHA-256 from those exact bytes.
4. Declare model/provider/runtime and prior-exposure/operator-relationship status.
5. Work only from the frozen challenge and public execution protocol until the raw reconstruction is complete.
6. Freeze the exact raw result before any target comparison.
7. Compute the raw-result SHA-256.
8. Create the cryptographic commitment before target comparison.
9. Preserve the exact raw bytes and commitment/reveal material required by the protocol.
10. Run the public structural verifier if available.
11. Submit the raw result, attestation v2, commitment/reveal evidence and provenance declaration.

## Semantic submission contract

The raw result MUST include:

- semantic factors/constructs and definitions;
- mapping for every frozen case;
- observable distinctions preserved;
- deletion/removal analysis;
- explicit composition rules;
- counterexamples and failure cases;
- uncertainty/unknown handling;
- declared minimality objective;
- explicit H4/no-finite-basis treatment;
- challenge criticism or omitted obligations, if any.

A smaller basis, different basis, irreducible residue, challenge criticism or H4/no-finite-basis result is admissible. Agreement with Genesis is neither required nor sufficient.

## Anti-laundering

Invalid reductions include:

- opaque containers renamed as primitives;
- case identifiers used as hidden semantics;
- undeclared relation labels carrying removed meaning;
- implementation metadata used as semantic content without declaration;
- evaluator-side dictionaries unavailable to the participant;
- changing the minimality objective after seeing a result.

## Blindness and contamination

If private target information is exposed before raw-result freeze, the participant MUST report contamination and MUST NOT present the run as a clean IR-V3 replication.

The coordinator MUST preserve contaminated, failed, contradictory and inconclusive runs rather than replacing them with favorable results.

## Acceptance states

- `RAW_BLIND_RUN` — raw result frozen; integrity/provenance still under review.
- `ATTESTED_EXECUTION` — attestation/integrity contract satisfied.
- `MATERIAL_EXTERNAL_INDEPENDENCE` — independent execution control and corroborating provenance are sufficient for the applicable gate.
- `CONTAMINATED` — blindness boundary breached before raw freeze.
- `UNKNOWN` — evidence insufficient for a stronger state.

This runbook is a procedure. It does not constitute evidence that any participant has executed IR-V3.
