# CI Probe — Execution Protocol

**Status:** ACTIVE DIAGNOSTIC CONTROL
**Date:** 2026-08-29
**Repository:** `nz-genesis/ci-probe`
**Canonical Genesis repository:** `nz-genesis/genesis-lab` (private)

## Purpose

Establish a minimal public control for GitHub-hosted Actions execution. The probe is deliberately Genesis-agnostic.

## Security boundary

This repository MUST NOT contain Genesis source, private corpus material, unpublished hypotheses, architecture, private evidence, credentials, tokens, secrets, or private configuration.

The repository is not a mirror of `genesis-lab`.

## Test contract

A valid execution must show, in order:

1. job assignment;
2. checkout step execution;
3. runtime identification;
4. deterministic probe execution producing `CI_PROBE_OK`;
5. artifact verification;
6. artifact upload.

A job that terminates before executable steps is classified as **execution-substrate failure**, not as a probe failure.

## Interpretation

### Public PASS

Evidence that this public repository successfully executed the specified workflow on the selected GitHub-hosted runner. It is **not Genesis evidence**.

### Public pre-step failure

Evidence that this public control could not obtain ordinary executable Actions execution. It does not identify the root cause by itself.

### Public PASS + private Genesis pre-step failure

Strong discriminator for a private repository / organization / account execution-context problem, subject to further confirmation.

### Public failure + private Genesis failure

Consistent with a broader Actions execution-substrate problem; additional controls are required before assigning root cause.

## Provenance

Every result must record:

- repository commit SHA;
- workflow run ID;
- job ID;
- runner label;
- job conclusion;
- whether executable steps are present;
- artifact presence where applicable.

Do not convert this external control into canonical Genesis evidence automatically.

## Promotion boundary

Any result imported into `genesis-lab` must retain its original provenance and remain explicitly classified as external evidence until accepted under the owning Genesis research protocol.
