# Coordinator Loss During Reconciliation — 2026-08-30

## Status
BOUNDED / EXPERIMENTAL / PUBLIC-CI PENDING

## Bounded question
Can loss of the reconciliation coordinator after a valid observation cause a duplicate effect when recovery resumes?

## Material novelty
This is not a replay, lost-ACK, shared-domain race, or stale-negative observation test. The discriminator is coordinator-state loss between observation and durable reconciliation record.

## Model
A durable effect already exists. The reconciler observes it, loses coordinator-local recording state, then recovers. Recovery rereads durable state rather than interpreting missing coordinator state as absence. A second operation identity remains distinct; a version change invalidates the old observation.

## Local result
COORDINATOR LOSS: RECONCILIATION RECOVERS WITHOUT DUPLICATE EFFECT
Assertions: 12/12 PASS

## Red Team
- Coordinator loss must not imply effect absence.
- Recovery must reread durable state.
- A stale negative snapshot cannot authorize retry.
- New operation identity remains distinct.
- Version change invalidates the old observation.
- Local fixture success is not production crash-consistency proof.

## Primitive reduction
No new Genesis primitive is demonstrated. The tested distinction is representable through durable state, operation identity, version constraints, uniqueness, and guarded transition/reconciliation.

## Evidence boundary
Executable artifact and workflow are present in this public clean-room repository. Exact hosted completion must be independently inspected before promotion to hosted-CI evidence.

## Omission gate
Still open: actual network partition, durable-storage crash boundary, coordinator replacement with divergent state, cross-domain effects, trust-root equivocation, private Genesis-to-public semantic correspondence, and external irreversible effects.

## Decision
Do not add a Genesis primitive. Do not open P190. Continue only with materially new failure semantics.
