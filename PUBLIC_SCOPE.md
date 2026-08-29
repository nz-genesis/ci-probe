# Public Experiment Boundary

This repository is a **public execution laboratory only**.

## Allowed

- generic GitHub Actions runner probes;
- deterministic, non-sensitive fixtures;
- generic execution/trigger/artifact tests;
- publicly reproducible observations about the CI substrate;
- generic test harnesses whose meaning does not depend on private Genesis internals.

## Forbidden

Never place here:

- Genesis source code or private implementation details;
- Genesis Lab research corpus, unpublished hypotheses, architecture decisions, or internal methodology;
- private prompts, fixtures, datasets, credentials, tokens, secrets, or customer data;
- private repository URLs or internal topology that is not already intentionally public;
- canonical Genesis state or canonical artifacts;
- private CI logs/artifacts copied from Genesis repositories;
- internal evidence whose publication would disclose unpublished Genesis development;
- credentials or configuration that could grant access to private Genesis systems.

## Evidence flow

The direction is intentionally one-way:

```text
public generic experiment
        ↓
public substrate observation
        ↓
private review / interpretation
        ↓
Genesis Lab evidence record
```

A result is **not** authoritative merely because the public experiment succeeded. The Genesis Lab record must preserve scope, provenance, interpretation, limitations, and epistemic status.

Do not automatically mirror Genesis Lab content into this repository.

## Execution safety

Workflows must use least-privilege permissions. Public workflows must not require Genesis secrets. Untrusted pull-request code must never receive private credentials or write access to Genesis repositories.

## Publication rule

When uncertain whether a file belongs here, treat it as private and keep it out of this repository until the Genesis Lab owner boundary explicitly determines that a public version is safe.
