# Private → Public Semantic Correspondence — 2026-08-31

**Status:** EXPERIMENTAL / EXECUTABLE / LOCAL PASS / HOSTED-CI PENDING

## Question
Can a private Genesis state expose a public semantic projection such that private-only mutations remain private while mutations to public semantics remain observable and distinguishable?

## Non-duplication
This is not a generic privacy test, cryptographic secrecy test, replay test, or physical-world execution test. The discriminator is correspondence between private semantic state and its externally consumable projection.

## Model
`PrivateState = public_status + public_version + private_note`.
The projection exposes only `(public_status, public_version)`.

## Local execution
The exact committed probe logic was independently reproduced in a clean Python environment.

`PRIVATE-PUBLIC CORRESPONDENCE: 4/4 PASS`

Cases:
1. changing only a private note does not change the public projection;
2. changing public status changes the projection;
3. changing public version changes the projection;
4. the private note is absent from the projection.

## Red Team / limits
This is deliberately a minimal information-flow surrogate. It does not prove arbitrary semantic preservation, cryptographic privacy, access-control completeness, differential privacy, or non-inference for complex data structures. A stronger future pass must use heterogeneous nested state and test whether derived public semantics accidentally leak private information.

## Primitive reduction
No new Genesis primitive is justified. `Projection`, `Redaction`, `PrivacyBoundary`, and `PublicState` remain behaviors/constraints over state, authority and evidence rather than new primitives.

## Decision
Bounded correspondence is locally supported. Canonical promotion is not implied. Hosted CI remains pending.

## Next discriminator
Strengthen this with derived-field noninterference: private mutations must not alter public outputs unless the mutated field is semantically declared public; conversely every public semantic mutation must produce an observable corresponding change. Then test this across nested state and authorization contexts.
