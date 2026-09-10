# Public Provenance Control — bounded execution experiment

**Status:** `EXPERIMENT / PUBLIC-SAFE CONTROL`

## Purpose

This experiment qualifies a public GitHub-hosted execution path for a generic deterministic provenance contract without publishing or transmitting private Genesis research material.

## What is public here

- a generic fail-closed verifier;
- a synthetic three-source frozen fixture;
- adversarial unit tests;
- a least-privilege GitHub Actions workflow.

## What is explicitly absent

- private Genesis corpus;
- private Genesis implementation;
- canonical Genesis decisions;
- unpublished hypotheses or reduction maps;
- credentials, secrets or private repository access.

## Acceptance boundary

A successful workflow can establish only:

1. the public runner executed the checked-in generic verifier;
2. the synthetic fixture passed the bounded integrity predicate;
3. the negative tests rejected the specified tampering classes;
4. the workflow ran with read-only repository permissions.

It does **not** establish private Genesis verifier execution, semantic equivalence, candidate blindness, material independence, or completion of any Genesis research gate.

## Negative tests

The test suite attacks:

- source-byte tampering;
- exact-span tampering;
- unknown source identifiers;
- repository-root escape;
- malformed manifest JSON;
- malformed claims JSONL;
- duplicate claim identifiers;
- malformed UTF-8 source bytes.

## Relation to private P400

The private P400 apparatus remains the authoritative research artifact in `genesis-lab`. This public experiment is only an external execution-substrate and generic-contract control. No private P400 data is required for this experiment.
