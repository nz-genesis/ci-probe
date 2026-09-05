# External Agent Execution Protocol v2

**Status:** `ACTIVE PUBLIC EXECUTION PROTOCOL / IR-V3`

## Purpose

Provide a fresh, blind, materially-independent execution route for IR-V3 after the provenance limitations of BIR-1A. This protocol is a procedure, not evidence that an independent participant has executed.

## Independence boundary

The participant may be an external AI-agent operator, research runner, or human using an external model/service. Public pseudonymity is allowed. Independence is adjudicated from execution control and provenance, not from anonymity.

The participant MUST NOT receive private Genesis research, the seven-element candidate, prior adjudication, BIR-1A results, or any target interpretation before the raw result is frozen.

A participant controlled by the Genesis operator may execute an apparatus test, but it is not eligible for L4 material independence merely because the execution occurs on another machine or provider.

## Fresh-run requirement

IR-V3 is a new frozen challenge. The participant must start from the exact public challenge bytes and must not reuse a previous reconstruction as the semantic answer. Reusing generic tooling is allowed only if the tool's prior target exposure is disclosed and the fresh semantic output is independently generated.

## Required sequence

1. Obtain `challenge-v3.json` and record its exact bytes.
2. Compute and record the challenge SHA-256 before semantic work.
3. Declare participant/model/provider/runtime provenance.
4. Declare prior Genesis exposure and relationship to the Genesis operator.
5. Generate the semantic reconstruction from the frozen challenge only.
6. Freeze the exact raw result before seeing or requesting any Genesis target interpretation.
7. Compute the raw-result SHA-256.
8. Create a cryptographic commitment over the raw-result digest and run identifier; the commitment MUST exist before target comparison.
9. Preserve the exact raw bytes and commitment material needed for later reveal.
10. Run the public structural verifier if available.
11. Submit the raw result, attestation and commitment/reveal evidence.

## Stronger provenance fields

The attestation should state, at minimum:

- stable participant ID;
- participant type;
- model family;
- model/provider identifier;
- runtime/version;
- execution-control mechanism at a non-sensitive level;
- solver/artifact digest where applicable;
- configuration digest where applicable;
- challenge SHA-256;
- raw-result SHA-256;
- commitment SHA-256;
- commitment creation time;
- execution start/end;
- prior Genesis exposure;
- operator relationship;
- whether raw output was frozen before target comparison;
- contamination status;
- any unavailable field and why.

Do not disclose credentials, API keys, hidden system prompts, private nonces before reveal, or sensitive personal information.

## Semantic contract

The participant must state:

- semantic factors/constructs;
- explicit definitions;
- mapping of every frozen case;
- observable distinctions preserved;
- deletion/removal analysis;
- explicit composition rules;
- counterexamples and failure cases;
- uncertainty/unknown cases;
- declared minimality objective;
- treatment of H4/no-finite-basis possibility.

The participant may reject the challenge or identify an omitted obligation. Such criticism is first-class evidence and must not be forced into a finite basis.

## Anti-laundering

Invalid reductions include:

- one opaque container renamed as a primitive;
- case identifiers used as hidden semantics;
- undeclared relation labels carrying removed primitive meaning;
- implementation metadata used as semantic content without declaration;
- evaluator-side dictionaries unavailable to the participant contract;
- changing the minimality objective after seeing the result.

## Adjudication states

`RAW_BLIND_RUN` → `INTEGRITY_VERIFIED` → `PROVENANCE_SUFFICIENT` → `MATERIAL_EXTERNAL_INDEPENDENCE` → `SEMANTIC_ADJUDICATION`.

Failure or uncertainty at any gate is preserved. It is never silently promoted to a stronger state.

## Red Team requirements

Attack at least:

- target leakage;
- prior Genesis exposure;
- operator/model correlation;
- post-hoc mutation;
- missing commitment;
- representation laundering;
- relation laundering;
- opaque factor reduction;
- hidden evaluator semantics;
- incomplete case coverage;
- unsupported H4 claims;
- unsupported independence claims.

## No target contamination after submission

Once the raw result is frozen, the coordinator must preserve it unchanged before revealing any private target interpretation. Semantic comparison occurs only after the provenance gate and must not rewrite the challenge or participant result.
