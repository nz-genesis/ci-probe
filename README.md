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
- HITL authority/risk/irreversibility boundaries.

The probes intentionally model semantic distinctions without introducing Genesis-specific engines or primitives.

## CI contract

Workflows perform only generic repository checkout and deterministic probe execution/regression. No external services or repository-specific secrets are required.

Results from this repository must be interpreted and, if warranted, canonicalized only in the private `nz-genesis/genesis-lab` repository.
