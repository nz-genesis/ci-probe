# External Agent Execution Protocol v1

**Status:** `ACTIVE PUBLIC EXECUTION PROTOCOL / IR-V2 COMPATIBLE`
**Purpose:** provide a public, blind, pseudonymous route for an external AI agent, human-operated agent, or independent research runner to execute IR-V2 without exposing private Genesis context.

## 1. Boundary

The public repository is an execution/evidence substrate, not a source of Genesis semantics.

The participant MUST derive its result from the frozen IR-V2 challenge and public protocol only. It MUST NOT receive the current seven-element basis, private Genesis reduction maps, private prompts, unpublished conclusions, or private adjudication context before raw-result freeze.

## 2. Pseudonymity

A participant MAY use a stable pseudonymous identifier instead of publishing a civil/legal identity.

Public anonymity does not by itself establish material independence. The participant should provide enough non-sensitive provenance to distinguish an independently controlled execution from a project-controlled or correlated run.

At minimum, the public attestation should disclose, where safely possible:

- stable pseudonymous participant ID;
- model/provider and declared version identifier, or explicit statement that this cannot be disclosed;
- execution/runtime identifier;
- solver/agent artifact digest if applicable;
- configuration digest if applicable;
- prior exposure to private Genesis material: `none / unknown / disclosed`;
- relationship to Genesis operator: `none declared / disclosed / unknown`;
- execution timestamp;
- exact challenge SHA-256;
- raw-result SHA-256;
- commitment/reveal evidence.

Do not publish API keys, credentials, private prompts, hidden system instructions, private nonces before reveal, or identifying personal information that is not necessary for adjudication.

## 3. Blind execution

Before raw-result freeze, the participant MUST:

1. obtain the exact frozen IR-V2 challenge;
2. verify its SHA-256;
3. independently derive its semantic factorization;
4. record coverage, deletion/reduction analysis, counterexamples, uncertainty and limitations;
5. freeze the raw result;
6. compute the raw-result SHA-256;
7. create the required cryptographic commitment;
8. preserve the exact raw bytes and nonce;
9. submit the public attestation metadata without target interpretation;
10. reveal the raw result only according to the agreed reveal procedure.

If private Genesis material is seen before raw freeze, mark the run `CONTAMINATED`.

## 4. Agent-specific rule

An external AI agent is eligible as a participant only if its execution path is genuinely outside the Genesis operator's controlled reasoning path.

Changing personas, prompts, system messages, temperature, model session, or labels inside the same controlled model/provider path is not sufficient material independence.

A hosted third-party model/provider may qualify as a materially different epistemic mechanism, but only when the execution provenance and non-contamination evidence are sufficiently corroborated for the applicable adjudication level.

A public GitHub Action running a Genesis-authored agent, prompt, solver, or model endpoint is not independent merely because it executes on GitHub-hosted infrastructure.

## 5. Public submission pattern

Preferred public submission is:

```text
independent-replication/submissions/<stable-pseudonym>/<run-id>/
```

The submission SHOULD contain:

- `ATTESTATION.md`;
- `raw-result.commitment` or equivalent commitment evidence;
- raw result after reveal;
- challenge SHA-256;
- raw-result SHA-256;
- verifier output;
- execution environment/provenance metadata;
- contamination statement;
- deviations/failures.

The participant may redact or withhold non-essential sensitive metadata while explicitly marking it `WITHHELD` rather than silently implying that it was verified.

## 6. Independence adjudication

Acceptance is staged:

```text
RAW_BLIND_RUN
    ↓
INTEGRITY_VERIFIED
    ↓
PROVENANCE_SUFFICIENT
    ↓
MATERIAL_EXTERNAL_INDEPENDENCE
    ↓
SEMANTIC ADJUDICATION
```

A pseudonymous submission can reach `MATERIAL_EXTERNAL_INDEPENDENCE` if its independent execution control and epistemic separation are sufficiently corroborated without requiring publication of civil identity. If those facts cannot be corroborated, the result remains useful raw/blind evidence but does not satisfy the material-independence gate.

Agreement with Genesis is not required. A smaller basis, different basis, additional irreducible distinction, challenge criticism, or non-finite-basis conclusion is valid evidence and must be preserved.

## 7. Red Team requirements

Every accepted submission must be attacked for:

- target leakage;
- hidden Genesis exposure;
- same-provider/same-operator correlation;
- oracle or solver circularity;
- post-hoc mutation;
- selective omission;
- representation laundering;
- basis-label anchoring;
- unsupported claims of independence;
- challenge incompleteness.

## 8. Non-circularity

The coordinator MUST NOT publish the target seven-basis or substantive adjudication before the participant's raw result is frozen.

The coordinator MUST preserve contradictory and unsuccessful submissions.

The protocol itself does not establish that any external agent has executed IR-V2.
