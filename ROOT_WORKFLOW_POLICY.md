# Root CI Workflow Policy

**Status:** ACTIVE GOVERNANCE
**Date:** 2026-09-04

## Main workflow

`.github/workflows/ci-probe.yml` is the repository-level substrate workflow.

Its green status means that the exact workflow steps executed for that exact commit completed successfully. It does not mean that every historical or experiment-specific probe in the repository has semantic support.

## Experiment-specific evidence

A conclusion about a specific probe must cite:

- the exact workflow filename;
- the exact triggering commit;
- the completed workflow run;
- the relevant job;
- the relevant step(s);
- logs/artifacts where required.

Do not infer semantic validity from the repository-level workflow alone.

## Historical workflows

A workflow whose owning surface is historical/control must use explicit manual dispatch unless there is a documented reason for automatic execution. This prevents historical regression runs from being mistaken for active research evidence.

## Active independent-replication workflow

The active independent reconstruction challenge is governed by `independent-replication/`. Its verification should remain separately identifiable from generic substrate smoke tests.

## Change discipline

When adding a new workflow:

1. identify its owning repository surface;
2. mark whether it is active, control or historical;
3. scope its path/event triggers to that surface;
4. keep permissions least-privilege;
5. document what a green run does and does not establish;
6. avoid duplicating a test already owned by another workflow.


## 7. Observed trigger fanout and inventory gap — 2026-11-07

A narrow change to the generic action-probe surface was pushed at commit 8fd5e9548859190fe9a8e95ae8de2035d7d4c5b6 (scenario workflow + scope documentation). GitHub created 63 workflow runs for that single push:

- 62 workflow runs completed successfully;
- one P385 external-ProvToolbox workflow run concluded failure with zero jobs, while its workflow definition has a push branch filter for main and the triggering branch was the feature branch; this is a no-job workflow-filter anomaly, not an executed P385 test;
- the dedicated Execution Scenario Matrix workflow completed successfully: run 42383762338, job 128436683588, 23 tests passed;
- the repository-level CI Probe smoke workflow completed successfully: run 42383762264.

A sample inspection of ci-probe.yml, pass40-effect-identity.yml, semantic-translation.yml, recovery-matrix.yml, pass48-crash-durable-state.yml and public-boundary.yml found unfiltered push triggers. This sample is not a complete inventory of the 196 workflow definitions present in the repository tree at the checked commit. Therefore no claim is made that all 62 experiment-specific workflows are incorrectly configured; ownership and trigger scope must be inventoried before broad remediation.

The new action-probe scenario workflow was corrected to use path-scoped push triggers for its owned source/tests/scope/evidence files, retained workflow_dispatch, and pinned actions/checkout v7.0.1 to commit 3d3c42e5aac5ba805825da76410c181273ba90b1 (Node 24). Its exact workflow/job result is above.

**Open follow-up:** inventory all workflow files by owning surface (ACTIVE / CONTROL / HISTORICAL), source/test dependencies, event triggers, path/branch filters, permissions and duplicate coverage. Keep the root ci-probe.yml repository smoke workflow distinct. Convert historical/control workflows to manual dispatch unless a documented exception exists; scope active experiment workflows to their actual source/test surface. Investigate the P385 no-job failure separately. Do not infer semantic support from unrelated successful workflow runs.
