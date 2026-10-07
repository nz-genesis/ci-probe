# Private CI Boundary Control Probe

**Status:** ACTIVE CONTROL EXPERIMENT  
**Scope:** public `ci-probe` only

## Purpose

This is the mandatory public control path for a private-repository workflow whose execution is restricted, unavailable, or otherwise cannot expose sufficient hosted evidence in the private repository.

The probe deliberately does not reproduce private Genesis source or semantics. It reproduces only the generic execution apparatus relevant to the infrastructure question.

## Current apparatus class

The current Genesis F2.3a private workflow requires:
- GitHub-hosted Ubuntu runner;
- exact triggering-commit checkout;
- Python 3.12;
- deterministic `unittest discover` execution.

This control checks those generic properties.

## Mandatory routing rule

When a private-repository CI experiment is blocked by repository visibility, permissions, unavailable dispatch/observation, private-only execution constraints, or equivalent evidence limitations, the owning research record MUST evaluate whether its execution apparatus can be reduced to a public-safe generic control.

If a safe reduction exists, the public control is mandatory:

`private evidence gap -> public ci-probe control -> raw hosted receipt -> private adjudication`

A local PASS may not substitute for this control.

If no safe reduction exists, the owning record MUST explicitly state why, preserve `INCONCLUSIVE`, and identify the missing evidence path.

## Interpretation

A successful run establishes only that the generic public execution apparatus tested by this control executed successfully.

It does not establish private Genesis scenario correctness, semantic equivalence, Genesis architecture, private permissions, or private secrets configuration.

## Required receipt

A public control counts only with:
- exact public repository;
- exact commit SHA;
- exact workflow;
- run ID;
- job ID;
- executed steps;
- relevant logs/artifacts;
- interpretation and limitations.

A workflow definition, queued run, or file existence is not execution evidence.
