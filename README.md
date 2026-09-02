# CI Probe

Minimal, Genesis-agnostic control repository for executable GitHub Actions experiments.

## Purpose

This repository exists only for generic executable experiments that can be run on public GitHub-hosted Actions runners.

It contains no Genesis source, private research corpus, private fixtures, hypotheses, architecture, unpublished findings, credentials, internal endpoints, datasets, or canonical decisions.

## Interpretation boundary

A successful run establishes only that the checked-out generic probe executes successfully on the selected runner and that its bounded assertions pass. It does **not** constitute Genesis evidence by itself and does not promote or modify any state in `nz-genesis/genesis-lab`.

A failed pre-step or substrate-related run is evidence about the execution environment and must not be interpreted as a Genesis test failure without further investigation.

## Current generic probes

The repository includes independent, bounded experiments covering:

- execution scenario outcomes;
- authority/revocation lifecycle;
- recovery after lost acknowledgement;
- idempotency-claim verification;
- concurrent/cross-realizer duplicate-effect risk;
- differential atomicity/coordination;
- adversarial contract/effect verification;
- HITL authority/risk/irreversibility boundaries;
- HITL approval × recovery composition.

The probes intentionally model semantic distinctions without introducing Genesis-specific engines or primitives.

## Blind factorization verification

`independence/` contains a Genesis-agnostic protocol for materially independent semantic factorization. The frozen neutral corpus exposes obligations but no Genesis primitive labels or target mapping. An external solver must submit anonymous factors (`F001`, `F002`, ...) and obligation coverage before private adjudication.

The public verifier checks only deterministic structural properties: corpus binding, opaque identifiers, complete coverage, duplicate/conflicting rows, and canonical submission hashing. It intentionally performs **no semantic adjudication**.

- Contract: `independence/README.md`
- Frozen corpus: `independence/neutral_corpus_v1.json`
- Submission schema: `independence/submission.schema.json`
- Structural verifier: `independence/verify_submission.py`

The public corpus is infrastructure, not Genesis evidence. A semantic result becomes evidence only after a genuinely independent solver/reviewer produces an immutable raw submission and the private Genesis repository performs the declared adjudication without leaking the target factorization beforehand.

## CI contract

Workflows perform only generic repository checkout and deterministic probe execution/regression. No external services or repository-specific secrets are required.

Results from this repository must be interpreted and, if warranted, canonicalized only in the private `nz-genesis/genesis-lab` repository.
