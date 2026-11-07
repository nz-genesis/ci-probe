# CI Probe — Repository Map

**Status:** ACTIVE GOVERNANCE / PUBLIC SUBSTRATE
**Date:** 2026-11-07

## Purpose

This file is the navigation and ownership map for the public repository. It prevents historical experiments, control surfaces and the active independent-replication channel from being mistaken for one evidence stream.

## Surfaces

| Path | Status | Role | Evidence boundary |
|---|---|---|---|
| independent-replication/ | **ACTIVE** | current clean-room reconstruction surface; IR-V2 | candidate-independent raw evidence; semantic adjudication occurs outside this repo |
| independence/ | **HISTORICAL / CONTROL** | earlier factorization verification surface | not a second independent evidence lineage |
| probes/ | **GENERIC / HISTORICAL-MIXED** | public executable experiments | each probe has its own bounded scope; not automatically part of IR-V2 |
| action_probe.py + action_probe/ | **ACTIVE / GENERIC** | consequential-action contract, exact admission binding, revocation recheck, unknown-state reconciliation and effect-certainty-aware retry matrix | exact workflow/run evidence; no private project semantics or external side effects |
| ACTION_PROBE_SCOPE.md | **ACTIVE GENERIC SCOPE** | boundary for generic consequential-action probe | generic execution substrate only |
| PUBLIC_SCOPE.md | **ACTIVE POLICY** | public/private boundary | controls what may be published |
| SECURITY.md | **ACTIVE POLICY** | security/confidentiality boundary | controls secrets/private material |
| .github/workflows/ | **EXECUTION** | hosted CI definitions | a workflow run proves only the steps it executes; individual runs must be referenced for execution claims |
| tools/ | **UTILITY** | generic verification helpers | utility code, not semantic evidence by itself |
| root *_PROBE* / probe scripts | **LEGACY / REVIEWED** | older generic substrate probes | retain until explicit deprecation/removal record exists; do not treat as the active semantic challenge |

## Active entrypoint

For independent reconstruction work, use only independent-replication/INDEPENDENT_REPLICATION_CALL.md and the exact frozen IR-V2 challenge revision specified there.

## Evidence counting

Different directories, workflows, prompts, corpus identifiers or process boundaries do not by themselves create independent evidence. Independence is established from information flow and provenance.

## Cleanup policy

Historical artifacts are preserved when they carry genealogy or negative-result value. Cleanup should normally mark status, establish current owner/entrypoint, remove stale navigation, disable accidental execution where safe, and delete only after provenance is preserved elsewhere.

## CI interpretation

The main ci-probe.yml workflow is a repository substrate workflow, not a universal semantic test suite. Experiment-specific conclusions must be tied to their exact workflow file and completed run.
