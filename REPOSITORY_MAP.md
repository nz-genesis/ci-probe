# CI Probe — Repository Map

**Status:** ACTIVE GOVERNANCE / PUBLIC SUBSTRATE
**Date:** 2026-09-05

## Purpose

This file is the navigation and ownership map for the public repository. It prevents historical experiments, control surfaces and the active independent-replication channel from being mistaken for one evidence stream.

## Surfaces

| Path | Status | Role | Evidence boundary |
|---|---|---|---|
| `independent-replication/` | **ACTIVE** | current clean-room reconstruction surface; IR-V2 plus experimental measurement protocols | may generate candidate-independent raw evidence; semantic adjudication occurs outside this repo |
| `independence/` | **HISTORICAL / CONTROL** | earlier factorization verification surface | not a second independent evidence lineage |
| `probes/` | **GENERIC / HISTORICAL-MIXED** | public executable experiments | each probe has its own bounded scope; not automatically part of IR-V2 |
| `.github/workflows/` | **EXECUTION** | hosted CI definitions | a workflow run proves only the steps it executes; individual runs must be referenced for execution claims |
| `tools/` | **UTILITY** | generic verification helpers | utility code, not semantic evidence by itself |
| root `*_PROBE*` / probe scripts | **LEGACY / REVIEWED** | older generic substrate probes | retain until explicit deprecation/removal record exists; do not treat as the active semantic challenge |
| `ACTION_PROBE_SCOPE.md` | **ACTIVE GENERIC SCOPE** | boundary for generic consequential-action probe | generic execution substrate only |
| `PUBLIC_SCOPE.md` | **ACTIVE POLICY** | public/private boundary | controls what may be published |
| `SECURITY.md` | **ACTIVE POLICY** | security/confidentiality boundary | controls secrets/private material |
| `independent-replication/RESOURCE_ENVELOPE_BENCHMARK_PROTOCOL.md` | **ACTIVE EXPERIMENTAL** | public resource-envelope measurement contract | generic measurements only; not semantic Genesis evidence by itself |

## Active entrypoint

For independent reconstruction work, use only:

`independent-replication/INDEPENDENT_REPLICATION_CALL.md`

and the exact frozen IR-V2 challenge revision specified there.

For resource-envelope economics, use the separately scoped `independent-replication/RESOURCE_ENVELOPE_BENCHMARK_PROTOCOL.md`. It must not modify or be counted as a second IR-V2 semantic challenge.

Do not infer active protocol state from directory names, filenames containing `V1`/`V2`, Git history or old root README references.

## Evidence counting

Different directories, workflows, prompts, corpus identifiers or process boundaries do not by themselves create independent evidence. Independence is established from information flow and provenance.

The `independence/` and `independent-replication/` surfaces belong to the same repository lineage and are not separate independent sources merely because their encodings differ.

## Cleanup policy

Historical artifacts are preserved when they carry genealogy or negative-result value. Cleanup should normally:

1. mark status explicitly;
2. establish current owner/entrypoint;
3. remove stale navigation/references;
4. disable accidental execution where safe;
5. delete only after provenance is preserved elsewhere and the deletion is explicitly justified.

## CI interpretation

The main `ci-probe.yml` workflow is a repository substrate workflow, not a universal semantic test suite. Experiment-specific conclusions must be tied to their exact workflow file and completed run. A green aggregate workflow must not be quoted as proof for an unrelated experiment.
