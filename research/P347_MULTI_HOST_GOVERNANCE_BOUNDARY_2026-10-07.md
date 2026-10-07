# P347 — Multi-Host Protected-Governance Boundary — 2026-10-07

## Status

EXECUTION ARTIFACT / RESULT PENDING

## Purpose anchor

Genesis global purpose is unchanged; see the canonical /AGENTS.md#0.

## Research question

Can an action-bearing Genesis composition preserve authority-sensitive effect safety when two genuinely separate execution hosts observe governance state, one host loses access to the authoritative service, governance changes independently, and the stale worker later reaches the consequential effect boundary?

## Admissible external substrate

The public nz-genesis/ci-probe repository is the established external execution/control substrate. GitHub-hosted Actions jobs are fresh VM instances for each job. The experiment uses worker A, authority client C and independent observer B on separate runner jobs; GitHub repository state is the external authoritative governance and protected effect boundary.

## Frozen core discriminator

Worker reads generation 1 and the exact protected-effect blob SHA; writes a real preparation artifact; creates and SIGKILLs a child process; blocks outbound HTTPS to api.github.com; authority mutates the protected gate to generation 2; worker resumes and attempts the old generation-1 update with the old blob SHA; the authoritative service must reject it with HTTP 409; an independent observer verifies the final state and runner identities.

## Evidence boundary

A successful run would establish real multi-VM execution for this substrate, real network isolation for the tested API addresses, independent governance mutation, stale-authority rejection at the actual effect boundary, real process-failure interleaving and independent observation.

It would not establish universal distributed consensus, arbitrary actuator safety, physical causality, Byzantine tolerance, universal exactly-once semantics, or behavior of arbitrary non-cooperating external systems.

## Primitive reduction hypothesis

H0: existing State + Transition + Capability + Authority + Observation + Evidence + Constraint remain sufficient; version/conditional-write behavior remains a realization mechanism.

H1: the multi-host protected-effect boundary reveals an irreducible semantic distinction not expressible by the current basis.

No new primitive is admitted before execution and reduction.

## TRIZ

Contradiction: local continuation and availability versus authoritative freshness and safe consequential effect.

IFR: permit safe local continuation and historical evidence during partition, but require authoritative state/version at the consequential effect boundary.

## Pre-registered Red Team

Fake multi-host identity; fake partition; stale authority acceptance; local state treated as authoritative; preparation mistaken for final effect; SIGKILL overclaimed as power-loss proof; GitHub conditional-write semantics overgeneralized; observer reading actor claims; candidate primitive leakage; unrelated branch race mistaken for semantic rejection; DNS/address churn leaving an API path open.

## Omission gate

INCONCLUSIVE until raw actor receipts, final authoritative state, distinct runner identities, exact triggering SHA, partition evidence, Red Team checks and primitive-reduction analysis are available.

## Downstream rule

If the run passes, update the Genesis Lab P347 owning architecture and decision ledger. Apparatus failures are repaired without changing semantic expectations. A stale effect that succeeds after the authority generation change is a material challenge to the current boundary and requires reduction analysis.


Execution apparatus freeze: e75c2ef0ae9c340ad9a54fc97f102b236819741f is the latest workflow commit after the token/path Red Team corrections.
