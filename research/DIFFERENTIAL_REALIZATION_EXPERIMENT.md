# Differential realization experiment

## Question

Can one implementation-independent semantic contract be realized through more than one mechanism while preserving the same externally relevant outcome?

## Frozen contract

Given request `req-001`, write value `v1` to key `item` and establish observable evidence that the requested value is present.

The contract deliberately does not prescribe execution topology, scheduling, queueing, API shape, process model, or programming language.

## Realizations

1. `direct`: apply the write immediately.
2. `queued`: place the write into a local queue and drain the queue before reporting the result.

Both are deterministic in this bounded experiment and use separate state stores.

## Compared evidence

The experiment compares:

- request identity;
- outcome (`applied`);
- observed resulting value (`v1`);
- resulting store state;
- realization provenance.

## Result interpretation

PASS means both mechanisms satisfy the frozen contract and produce equivalent bounded outcome/effect evidence while retaining mechanism provenance.

It does **not** prove semantic equivalence of arbitrary implementations, reliability under failure, idempotency, concurrency safety, authority, external-world effect, or universal execution semantics.

## Epistemic status

`OBSERVED / BOUNDED EXPERIMENT`
