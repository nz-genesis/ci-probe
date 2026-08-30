# Non-Idempotent Timeout Recovery — 2026-08-31

**Status:** EXPERIMENTAL / EXECUTABLE / LOCAL PASS / HOSTED-CI PENDING / NEGATIVE BOUNDARY

## Question
Can recovery safely choose retry or no-retry after an external non-idempotent call times out when the local executor state is identical whether the external effect already happened or did not happen?

## Non-duplication
This is not another atomicity or coordinator-loss test. The discriminator is an indistinguishability/impossibility boundary: two externally different histories produce the same local timeout observation.

## Model
Two worlds are possible after the same timeout: effect count is already `1`, or effect count is `0`. The recovery actor sees only the same operation id and missing acknowledgement. Retrying adds an effect; not retrying leaves the zero-effect world incomplete.

## Local result
The exact committed probe logic was independently reproduced in a clean Python environment:

`NON-IDEMPOTENT TIMEOUT IMPOSSIBILITY: 4/4 PASS`

## Red Team
The test explicitly constructs both indistinguishable histories and checks both recovery choices:
- retry duplicates the effect in the already-affected world;
- no-retry misses the effect in the not-yet-affected world.

Therefore no recovery policy based only on the local timeout state can be safe in both histories.

## Semantic result
This is a negative boundary result, not a proposed primitive. Safe recovery requires additional information or a stronger external contract, such as independently queryable effect identity/state or provider-side idempotency/transaction semantics.

## Primitive reduction
No new Genesis primitive is justified. The impossibility arises from missing information/contract guarantees, not from a missing `RecoveryEngine`, `ExternalWorld`, `ExactlyOnce`, or `TimeoutResolver` primitive.

## Limits
The model is bounded and abstracts away provider-specific transactional semantics and physical-world observation.

## Decision
The distinction strengthens the external-realization boundary: execution timeout cannot by itself determine external effect state. Canonical promotion is unaffected.

## Next discriminator
Do not repeat the same impossibility test. Test whether an independently queryable effect identity is sufficient to collapse the ambiguity, and whether a provider without idempotency still requires an explicit unresolved/UNKNOWN outcome rather than an unsafe retry.
