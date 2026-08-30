# Network Partition Reconciliation — 2026-08-30

## Status
BOUNDED / LOCAL MODEL PASS / HOSTED CI PENDING

## Question
Can two recovery actors holding the same stale observation during a network partition independently authorize a duplicate irreversible effect?

## Novelty
This is not a replay test, lost-ACK test, stale-negative single-actor test, or coordinator-loss test. The discriminator is simultaneous stale observations held by two actors while communication is unavailable, followed by reconciliation after partition healing.

## Model
A single authoritative durable commit domain contains the operation identity, version, and effect state. During partition, actors A and B cannot observe updates made after their snapshot. Both hold the same stale `(op, version)` token. The commit gate consults current durable state before allowing an effect. Once the partition heals, both actors reread current durable state.

## Local result
`NETWORK PARTITION: STALE RECOVERY CANNOT DUPLICATE DURABLE EFFECT`
`15/15 PASS`

## Red Team
1. Partitioned stale snapshots are not treated as independent authority.
2. Matching stale tokens do not authorize a commit when current durable effect already exists.
3. Both actors reconcile after healing.
4. Fresh operation identity remains distinct.
5. Version change invalidates both old snapshots.
6. This fixture does not prove a real network partition, consensus, Byzantine tolerance, or physical-world exactly-once semantics.

## Primitive reduction
No new Genesis primitive is demonstrated. The tested distinction remains expressible through durable state, operation identity, version constraints, uniqueness, authoritative commit gating, and reconciliation.

## Evidence boundary
Executable public artifact and workflow are present. Hosted completion must be independently inspected before claiming public-CI verification.

## Decision
Do not add a Genesis primitive. Do not open P190. Continue only if a materially different discriminator remains.

## Next discriminator
If warranted: coordinator replacement with divergent state / authority equivocation. Do not repeat generic replay or single-domain races.
