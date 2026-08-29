# CI Probe

Minimal, Genesis-agnostic control experiment for GitHub Actions execution.

## Purpose

This repository exists only to distinguish ordinary public GitHub-hosted Actions execution from repository-specific execution failures.

It contains no Genesis source, research corpus, private fixtures, hypotheses, architecture, unpublished findings, credentials, or private configuration.

## Interpretation

A successful run establishes only that this public repository can execute the probe on the selected GitHub-hosted runner. It does **not** constitute Genesis evidence and does not promote or modify any state in `nz-genesis/genesis-lab`.

A failed pre-step run is evidence about the execution substrate and must not be interpreted as a Genesis test failure without further investigation.

## Probe contract

The workflow intentionally performs only:

1. checkout;
2. runtime identification;
3. deterministic probe execution;
4. artifact generation.

No external services or repository-specific secrets are required.
