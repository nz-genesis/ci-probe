# Recovery matrix experiment

## Scope

Clean-room, Genesis-agnostic executable experiment. It extends the previous successful-case differential realization experiment into recovery conditions; it does not alter or encode Genesis architecture.

## Frozen request contract

For request `req-001`, establish the requested value `v1` at two keys, `item-a` and `item-b`, version `1`, and retain enough observable information to classify the resulting condition.

The two-effect contract is deliberate: it makes `partial` semantically observable rather than merely a label attached to a complete single-key effect.

Two realization mechanisms are compared:

- `direct` — immediate local application;
- `queued` — local queue/drain realization.

The mechanisms receive the same injected condition and must produce the same bounded classification. Mechanism provenance remains explicit.

## Conditions

| Condition | Effect count | Acknowledgement | Observation | Recovery classification |
|---|---:|---:|---|---|
| success | 2 | yes | both values/version confirmed | success |
| failed before effect | 0 | yes | no requested effect | failed |
| partial | 1 of 2 | yes | one value present, one absent | partial |
| acknowledgement lost | 2 | no | requested effect not directly confirmed | unknown |
| duplicate effect | 3 | yes | repeated effect detectable | duplicate |
| stale version | 0 | yes | older state remains | stale |
| revoked before realization | 0 | no | no realization permitted | revoked |

## Discriminating question

Does recovery require a new semantic primitive, or can the necessary distinctions be represented through state/transition/observation/evidence/constraint plus policy/reconciliation operations?

## Observed result

Both realization mechanisms preserve the same bounded classification for all seven injected conditions. The experiment therefore provides no evidence that mechanism identity itself is a required semantic distinction for recovery classification.

The stronger result is about the **recovery information boundary**:

- `UNKNOWN` cannot be safely converted to `FAILED` merely because acknowledgement is absent;
- `UNKNOWN`, `PARTIAL`, and `DUPLICATE` require reconciliation rather than blind retry in this contract;
- `FAILED` is retryable only because the fixture explicitly establishes no effect;
- `STALE` and `REVOKED` are distinct from `FAILED` because their meaning is not simply absence of effect;
- an acknowledgement remains distinct from evidence of the requested effect.

## Red-Team correction history

The first implementation of this bounded pass used a single-key request while labeling one effect as `partial`. Red Team identified that as a semantic modeling flaw: a single-key write cannot demonstrate partial completion of the requested contract. The fixture was corrected to a two-key contract and a regression test was added requiring one-of-two effects for `partial`.

The initial flawed implementation is historical evidence only and is superseded by the corrected experiment. It must not be counted as independent evidence.

## Epistemic status

`OBSERVED / BOUNDED EXPERIMENT`.

This is not a universal theorem about distributed systems or external-world actions.

## Deliberate limitations

The fixture does not model persistent storage, independent observers, concurrent actors, network partitions, clocks, authority, physical effects, durable queues, crash recovery, or causal attribution. Those dimensions remain for subsequent bounded research.

## Public boundary

No Genesis source, private architecture, private hypotheses, credentials, internal endpoints, datasets, or canonical decisions are included. Interpretation and canonicalization remain in private `genesis-lab`.
