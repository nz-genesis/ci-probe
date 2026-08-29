# Concurrency / idempotency experiment

## Scope

Clean-room, Genesis-agnostic executable experiment. This pass follows the recovery matrix and asks whether duplicate-effect prevention is a semantic requirement or merely a mechanism-specific implementation feature.

## Two contracts

### Contract F — final state

After repeated realization attempts for request `req-001`, the requested value `v1` is established.

### Contract E — effect cardinality

The same request produces **at most one external effect**.

These contracts are deliberately separated. A system may satisfy Contract F while violating Contract E.

## Realizations

1. `naive` — every attempt produces the effect.
2. `deduplicating` — a stable request identity suppresses repeated effects.

## Schedules

Two deterministic interleavings are enumerated:

- attempt-1 → attempt-2;
- attempt-2 → attempt-1.

A separate schedule models retry after a lost acknowledgement.

This is an interleaving model, not a claim of real parallel CPU execution.

## Observed result

For both interleavings:

| Mechanism | Final state | Effect count |
|---|---|---:|
| naive | `v1` | 2 |
| deduplicating | `v1` | 1 |

For lost-acknowledgement retry the same distinction appears: both mechanisms establish the same final state, but only the deduplicating mechanism preserves the at-most-one-effect contract.

## Discriminating conclusion

This is evidence that **idempotency/effect cardinality can be a semantic contract requirement even when realization mechanism remains implementation-dependent**.

It does **not** establish that `Idempotency` is a Genesis primitive.

The result instead supports a reduction path in which:

```text
semantic contract / constraint
        ↓
required effect cardinality
        ↓
mechanism-specific realization strategy
```

A mechanism must provide whatever implementation behavior is necessary to satisfy the contract, but its internal deduplication strategy need not become a Genesis primitive.

## Important boundary

If the contract only requires final state, the naive mechanism passes this bounded test. If the contract requires at-most-once effect, it fails. Therefore the semantic distinction comes from the **required guarantee**, not automatically from the mechanism.

## Epistemic status

`OBSERVED / BOUNDED EXPERIMENT`.

## Limitations

No actual distributed race, durable external effect, network partition, process crash, multi-node clock, authority race, or physical-world effect is modeled. A stronger pass is required before any claim about universal idempotency or concurrency safety.

## Public boundary

No Genesis source, private hypotheses, canonical decisions, credentials, internal endpoints, or private datasets are included. Interpretation remains in private `genesis-lab`.
