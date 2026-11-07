# CI Probe

Public, Genesis-agnostic execution and independent-replication substrate.

## Purpose

This repository contains only deliberately public, generic experiments and infrastructure that can run on public GitHub-hosted Actions runners. It must not contain private Genesis source, private research corpus, private prompts/fixtures, unpublished hypotheses, canonical decisions, credentials, private datasets, or internal endpoints.

## Repository map

See [REPOSITORY_MAP.md](REPOSITORY_MAP.md) for ownership, active/historical boundaries and evidence-counting rules.

    ROOT
    ├── probes/                     generic executable probes
    ├── tools/                      generic verification utilities
    ├── action_probe/               active generic action scenario matrix
    ├── independence/               historical/control factorization surface
    ├── independent-replication/    ACTIVE clean-room replication surface
    └── .github/workflows/          public CI workflows

## Active clean-room replication

The only active entrypoint for materially independent reconstruction is independent-replication/. Use its current frozen challenge and runbook. The older independence/ directory is a historical/control surface, not a second independent evidence lineage.

## Evidence boundary

A successful public run establishes only the behavior checked by that public artifact. It does not establish any private Genesis semantic claim by itself. Public execution evidence may be reviewed and imported into the private research corpus only with explicit provenance and epistemic scope. No automatic write-back is permitted.

## Current generic probes

The repository contains bounded probes for execution, authority/revocation, recovery, idempotency, concurrency, external-effect reconciliation, adversarial evidence and related generic substrate behavior. The active action probe tests exact admission binding, revocation at dispatch, unknown-state reconciliation and effect-certainty-aware retry candidates. Other probes separately cover late evidence, artifact closure, external-effect recovery and evidence-scope binding. These are independent experiments, not a cumulative semantic proof.

- [Generic atomic file publication probe](probes/atomic_file_publication_macos.py) — macOS ARM64 / Python 3.14 observation of staged file writes, fsync, exclusive hard-link publication, permission denial, concurrent publishers, process termination and ancestor-path replacement; generic OS substrate only.

## Continuous integration

See ROOT_WORKFLOW_POLICY.md. The generic ci-probe workflow is not a universal semantic test suite. Experiment-specific conclusions must be tied to exact workflow runs, jobs and logs.

## Security

See PUBLIC_SCOPE.md and SECURITY.md for the public/private boundary and execution safety rules.
