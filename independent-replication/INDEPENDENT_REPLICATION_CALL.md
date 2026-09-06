# Call for Independent Reconstruction

This repository hosts a public clean-room challenge for researchers and independent AI-agent operators who want to independently reconstruct a minimal semantic basis from a neutral set of obligations.

## Active challenge

Use **IR-V3**: `challenge-v3.json`.

Frozen challenge identity:

- `challenge_id`: `IR-V3`
- `schema_version`: `3.0.0`
- frozen commit: `3d37e023b49a995b466954445c1672f5d7ef046d`
- content SHA-256: `50f41fdc1a7d563367fb07316f2c84adc95c74a0`

This is the SHA-256 of the exact `challenge-v3.json` bytes. The participant MUST recompute the digest from the exact bytes received. Do not substitute a Git blob SHA-1 or commit SHA where the protocol requires the content SHA-256.

**Do not use `challenge-v2.json` for an IR-V3 submission.** IR-V2 remains preserved as historical research infrastructure and auxiliary evidence only.

## What is being tested

The task is **not** to reproduce a supplied ontology. The participant receives a frozen challenge containing bounded obligations and adversarial cases, then derives their own semantic factorization.

A materially different result is valid and useful. In particular, participants may conclude that:

- a smaller basis is sufficient;
- a different basis is required;
- an additional distinction is irreducible;
- the challenge is incomplete, biased, circular, or under-specified;
- the problem does not admit a finite universal basis under the tested assumptions.

## Independent AI-agent route

An external AI agent, human-operated agent, or independent research runner may participate through the active public procedure in:

`EXTERNAL_AGENT_EXECUTION_PROTOCOL_V2.md`

and:

`EXTERNAL_PARTICIPANT_RUNBOOK_V2.md`

Public pseudonymity is permitted. It does **not** automatically establish material independence; the run still requires sufficient execution-control and provenance evidence for adjudication.

## Independence requirement

For the strongest result, the participant should not inspect private research, a target basis, or unpublished reduction maps before freezing the raw reconstruction.

Changing prompts or personas within the same reasoning path is not considered material independence.

## Required result

Submit:

1. the independently derived basis and definitions;
2. case-by-case coverage of the frozen IR-V3 challenge;
3. removal/reduction analysis;
4. explicit composition rules;
5. structured adversarial counterexamples;
6. uncertainty and limitations;
7. explicit H4/no-finite-basis treatment;
8. provenance and candidate-visibility statement;
9. the exact `challenge_sha256`;
10. a cryptographic commitment to the raw submission before comparison;
11. the raw submission after the agreed reveal;
12. execution attestation v2 and verifier output.

## Evaluation

The structural verifier checks reproducibility and schema integrity. It intentionally does not contain a target ontology, a target category list, or a required semantic vocabulary, and it does not decide semantic adequacy.

After reveal, the reconstruction can be compared with other hypotheses. Agreement is not required for a valid result. Disagreement is first-class evidence and should be accompanied by an explicit explanation of the disputed obligation or distinction.

## Challenge limitations

The published challenge is bounded. It does not establish that its obligations exhaust the semantic space. Participants are explicitly encouraged to identify omitted domains, obligations, or counterexamples.

## Security

Do not submit secrets, credentials, private datasets, private research, or unpublished authority material.

## Repository boundary

This public repository is only an independent execution and replication surface. It does not contain private Genesis research or canonical Genesis state. Any resulting interpretation must remain separate from the participant's raw evidence.
