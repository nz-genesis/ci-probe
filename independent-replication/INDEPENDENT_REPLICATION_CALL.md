# Call for Independent Reconstruction

This repository hosts a public clean-room challenge for researchers who want to independently reconstruct a minimal semantic basis from a neutral set of obligations.

## What is being tested

The task is **not** to reproduce a supplied ontology. The participant receives a frozen challenge containing bounded obligations and adversarial cases, then derives their own semantic factorization.

A materially different result is valid and useful. In particular, participants may conclude that:

- a smaller basis is sufficient;
- a different basis is required;
- an additional distinction is irreducible;
- the challenge is incomplete, biased, circular, or under-specified;
- the problem does not admit a finite universal basis under the tested assumptions.

## Independence requirement

For the strongest result, the participant should not inspect private research, a target basis, or unpublished reduction maps before committing their reconstruction.

Changing prompts or personas within the same reasoning path is not considered material independence.

## Required result

Submit:

1. the independently derived basis and definitions;
2. case-by-case coverage of the frozen challenge;
3. removal/reduction analysis;
4. structured adversarial counterexamples;
5. uncertainty and limitations;
6. provenance and candidate-visibility statement;
7. the exact `challenge_sha256`;
8. a cryptographic commitment to the raw submission before comparison;
9. the raw submission after the agreed reveal point;
10. verifier output and execution environment.

## Evaluation

The structural verifier checks reproducibility and schema integrity. It intentionally does not contain a target ontology and does not decide semantic adequacy.

After reveal, the reconstruction can be compared with other hypotheses. Agreement is not required for a valid result. Disagreement is first-class evidence and should be accompanied by an explicit explanation of the disputed obligation or distinction.

## Challenge limitations

The published challenge is bounded. It does not establish that its obligations exhaust the semantic space. Participants are explicitly encouraged to identify omitted domains, obligations, or counterexamples.

## Security

Do not submit secrets, credentials, private datasets, private research, or unpublished authority material.

## Repository boundary

This public repository is only an independent execution and replication surface. It does not contain private Genesis research or canonical Genesis state. Any resulting interpretation must remain separate from the participant's raw evidence.
