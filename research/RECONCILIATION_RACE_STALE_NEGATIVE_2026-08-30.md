# Reconciliation Race — Stale Negative Observation — 2026-08-30

## Status

BOUNDED / EXPERIMENTAL / HOSTED-CI PENDING

## Question

Can a stale negative observation (`effect_count = 0`) cause a duplicate irreversible effect when another actor commits the same operation before the observer retries?

## Relation to prior work

This is not a replay-only test. Prior work established that verifier-local freshness is insufficient across independent verifiers, and that one shared coordination domain can enforce one-time consumption in the tested model. Prior lost-ACK work established that durable effect and acknowledgement delivery are distinct. This pass specifically tests the race between a negative observation and a concurrent durable commit.

## Generic model

Actor A observes `(commitment=c-1, version=7, effect_count=0)`. Actor B then commits the same commitment at version 7, producing `effect_count=1`. Before A retries, reconciliation reads the current state. The retry guard therefore evaluates false because the durable effect is already present. A later authority/version change also makes the old observation stale.

The fixture contains no `stale`, `race`, `duplicate`, `reconciled`, or semantic-status input labels.

## Red Team

1. Negative observation is treated as permanently authoritative: rejected.
2. Retry is allowed without reconciliation: rejected.
3. Authority/version change is ignored: rejected.
4. Substituted commitment is accepted as the original operation: rejected.

## Result

The bounded model blocks the duplicate caused by a stale negative observation when the retry performs current-state reconciliation before commit.

## Non-claims

This does not prove production crash safety, distributed consensus, network-partition tolerance, Byzantine resistance, physical-world effect correctness, or universal exactly-once semantics. It is a bounded generic model only.

## Primitive reduction

No new Genesis-level primitive follows. The tested distinction is representable using operation identity, current durable state, version/authority constraints, uniqueness and a guarded state transition.

## Next discriminator

Do not repeat replay, generic temporal, relational, or single-domain race tests. The next materially new boundary is coordinator loss / network partition during reconciliation, followed by cross-domain consumption only if warranted.
