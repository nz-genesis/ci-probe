# Execution substrate boundary — 2026-08-30

## Purpose
Record the public clean-room control relevant to the private Genesis Lab Actions blocker.

## Scope
This document contains only generic executable evidence. It contains no private Genesis hypothesis, architecture decision, credential, endpoint, dataset, or canonical decision.

## Observed public control

Repository: `nz-genesis/ci-probe`
Workflow: `Dynamic Delegation`
Run: `33279900685`
Job: `99173194389`

Observed job steps:

- `Set up job` — completed / success
- `Checkout` — completed / success
- `Execute dynamic delegation experiment` — completed / success
- `Post Checkout` — completed / success
- `Complete job` — completed / success

## Interpretation boundary

This proves that a public clean-room repository under the same organization can obtain a GitHub-hosted runner and execute workflow steps at this time.

It does **not** prove that the private `genesis-lab` repository has the same Actions policy, billing/quota state, environment protections, permissions, or execution eligibility. It also does not replace private canonical verification and is not Genesis architecture evidence.

## Research consequence

The public control is sufficient to establish runner availability at the organization/public-repository substrate level for this observed run. Remaining P189 blocker is private-repository/account execution eligibility. Do not create additional public semantic experiments merely to compensate for the private blocker.
