# Crash-after-durable-commit / ambiguous acknowledgement — 2026-08-30

## Purpose
Bounded verification of the failure mode where a durable effect occurs but its acknowledgement is lost. This is a follow-up to crash-before-commit recovery and shared-domain consumption; it does not repeat either test.

## Question
Can recovery distinguish `effect durable + ACK lost` from `effect not durable`, reconcile the durable observation, reject an unsafe duplicate, and reject a stale retry after an authority/version change?

## Model
The fixture separates durable effect state from acknowledgement delivery. `commit_and_lose_ack()` records the effect but returns no acknowledgement. `reconcile()` reads durable state. `retry()` is guarded by current version and uniqueness. The model then changes version to test stale retry rejection and permits an unrelated fresh nonce under the new version.

## Expected properties
1. durable effect may exist without an acknowledgement;
2. reconciliation observes the durable effect;
3. retry of the same commitment/nonce is rejected;
4. actor substitution is rejected;
5. stale retry under an old version is rejected;
6. an unrelated current-version nonce remains admissible.

## Local result
The bounded probe is designed for 8/8 assertions, including the above six semantic properties and state-cardinality checks.

## Red Team
Attack A: treat missing ACK as missing effect. Rejected by explicit durable reconciliation.

Attack B: retry before reconciliation. Rejected by durable uniqueness in the bounded model.

Attack C: substitute actor identity for the same effect. Rejected by the same durable key.

Attack D: reuse stale authority/version after the version changes. Rejected by the retry precondition.

Attack E: infer production exactly-once behavior from an in-memory set. Explicitly rejected. This artifact does not model process crash, storage atomicity, network partition, or Byzantine behavior.

## Primitive reduction
No new Genesis primitive is justified by the bounded model. The tested distinction is representable as durable state, identity/uniqueness, version constraints, reconciliation observation, and transition guards. This is not a global minimality proof.

## Canonical impact
Global Purpose: unchanged.
Genesis ontology: unchanged.
Canonical architecture: unchanged.
New Genesis primitives: 0.
P190: not started.

## Omission gate
Remaining materially distinct failures include reconciliation race, coordinator loss, network partition, Byzantine or equivocal observers, cross-domain atomicity, and multi-resource non-commutative effects. Do not repeat crash-before-commit or single-verifier replay experiments.

## Status
BOUNDED / LOCAL MODEL until exact hosted workflow execution is independently inspected.
