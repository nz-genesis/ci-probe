# Crash-after-prepare recovery — 2026-08-30

## Status
BOUNDED EXPERIMENTAL RESULT / LOCAL EXECUTION REQUIRED BEFORE PROMOTION.

## Question
Does separating volatile preparation from durable consumption permit safe recovery after a crash immediately after preparation, while preserving one-time consumption and rejecting stale recovery attempts?

## Scope
Clean-room coordination model only. This does not define a Genesis primitive, canonical runtime, cryptographic protocol, or production distributed transaction mechanism.

## Model
The fixture contains opaque actor/commitment/nonce identifiers and numeric versions. `prepare` checks the admissible pre-state but does not mutate durable consumption state. `crash_after_prepare` discards only the volatile preparation state. `commit` is the durable consumption transition and is idempotent for the same commitment/nonce. A version change invalidates an old recovery precondition.

## Expected properties
1. A crash after successful prepare does not create a consumption.
2. Recovery can repeat prepare.
3. Exactly one durable commit is possible for the same commitment/nonce.
4. A post-commit retry is rejected.
5. A second actor cannot turn the same consumed item into another commit.
6. Recovery using a stale version is rejected.

## Local test command
`python3 crash_recovery_shared_consumption.py`

Expected output: `CRASH AFTER PREPARE RECOVERY: 8/8 PASS`.

## Red Team
The main attack is to conflate prepare with durable consumption. The fixture prevents that by making the crash discard preparation without changing the consumed set. A second attack is to let recovery reuse a stale authority/version observation; this is rejected by the commit precondition. A third attack is duplicate delivery after durable consumption; both prepare and commit reject it.

## Limits
This bounded model does not establish correctness under process death during an actual storage commit, network partitions, coordinator loss, Byzantine participants, multi-resource atomicity, or cross-domain recovery. Those require distinct experiments and must not be inferred from this result.

## Primitive-reduction result
No new Genesis primitive is justified. The tested distinction is representable by state, version constraints, and a durable transition with uniqueness.

## Canonical impact
Global Purpose: unchanged.
Genesis ontology: unchanged.
Canonical architecture: unchanged.
New Genesis primitives: 0.
P190: not started.

## Next discriminator
If the hosted result passes, the next non-duplicate test is crash during/after durable commit with ambiguous acknowledgement, followed by retry and independent observer reconciliation. Do not repeat crash-after-prepare once this bounded question is verified.
