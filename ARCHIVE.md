# CI Probe — Archive and Active-Surface Policy

**Status:** ACTIVE GOVERNANCE
**Date:** 2026-09-04

## Active public surface

The active public independent-replication surface is:

`independent-replication/`

The currently active challenge is IR-V2. Its exact challenge revision and content SHA-256 are authoritative for a replication run.

## Historical / control surfaces

The following are retained for genealogy, regression history or control experiments and are **not** independent evidence lineages by themselves:

- `independence/` — historical blind-factorization/control surface;
- root-level legacy probe scripts;
- experiment-specific historical workflows whose scope is not part of the active replication contract;
- proposal/design notes explicitly marked `SUPERSEDED`, `HISTORICAL`, `CONTROL` or `NOT ACTIVE`.

Retention does not imply current validity.

## Safe cleanup rule

A historical artifact is removed only when all of the following are true:

1. its provenance/genealogy is preserved in an appropriate record;
2. it has no active consumer or workflow dependency;
3. its deletion does not destroy reproducibility of a still-open result;
4. the deletion itself is documented.

Until those conditions are established, prefer explicit archival status and disable accidental execution rather than deleting evidence.

## Workflow policy

Experiment-specific workflows must be scoped to their owning active surface. Historical/control workflows must not run on ordinary repository pushes unless their execution is intentionally requested as a regression/control action.

A repository-wide smoke workflow must never be presented as proof of a specific research pass.

## Evidence interpretation

A CI run is evidence only for the exact workflow definition, commit, job and steps that executed. Repository organization, filename, or green aggregate status does not create semantic evidence.
