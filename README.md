# CI Probe

Public, Genesis-agnostic execution and independent-replication substrate.

## Purpose

This repository contains only deliberately public, generic experiments and infrastructure that can run on public GitHub-hosted Actions runners. It must not contain private Genesis source, private research corpus, private prompts/fixtures, unpublished hypotheses, canonical decisions, credentials, private datasets, or internal endpoints.

## Repository map

See [`REPOSITORY_MAP.md`](REPOSITORY_MAP.md) for ownership, active/historical boundaries and evidence-counting rules.

```text
ROOT
├── probes/                     generic executable probes
├── tools/                      generic verification utilities
├── independence/               historical/control factorization surface
├── independent-replication/    ACTIVE clean-room replication surface
└── .github/workflows/          public CI workflows
```

### Active clean-room replication

The **only active entrypoint for materially independent reconstruction is**:

`independent-replication/`

Use its current frozen challenge and runbook. The active public call is the IR-V2 challenge described in `independent-replication/INDEPENDENT_REPLICATION_CALL.md`.

The older `independence/` directory is retained as a historical/control surface. It is not a second independent evidence lineage and must not be treated as the current replication entrypoint.

## Evidence boundary

A successful public run establishes only the behavior checked by that public artifact. It does not establish any private Genesis semantic claim by itself. Public execution evidence may be reviewed and, when warranted, imported into the private Genesis research corpus with explicit provenance and epistemic scope.

The intended flow is:

```text
public generic artifact
        ↓
public execution / raw evidence
        ↓
private review + adjudication
        ↓
Genesis Lab evidence record
```

No automatic write-back to `nz-genesis/genesis-lab` is permitted.

## Current generic probes

The repository contains bounded probes for execution, authority/revocation, recovery, idempotency, concurrency, external-effect reconciliation, adversarial evidence and related generic substrate behavior. These are historical or generic execution artifacts, not a single cumulative semantic proof.

## Continuous integration

See [`ROOT_WORKFLOW_POLICY.md`](ROOT_WORKFLOW_POLICY.md).

`.github/workflows/ci-probe.yml` is the generic repository smoke/substrate workflow. It must not be interpreted as a universal semantic test suite. Experiment-specific workflows remain separately scoped and their individual run conclusions must be reported from their exact workflow run, job and logs.

## Security

See `PUBLIC_SCOPE.md` and `SECURITY.md` for the public/private boundary and execution safety rules.
