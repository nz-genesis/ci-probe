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
