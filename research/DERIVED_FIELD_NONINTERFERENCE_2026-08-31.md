# Derived-Field Noninterference — 2026-08-31

**Status:** EXPERIMENTAL / EXECUTABLE / LOCAL PASS / HOSTED-CI PENDING

## Question
Does the private→public boundary remain stable when private fields change and when a private field could otherwise be incorporated into a derived public output?

## Non-duplication
This extends the 2026-08-31 minimal private→public correspondence probe. It is not a replay or generic privacy test. The discriminator is noninterference of private mutations with the declared public projection.

## Model
State contains public status/version and private note/score. The public projection exposes only declared public semantics. Two private-only mutations must preserve the projection; public-semantic mutations must change it; private fields must not appear in the output.

## Local execution
The exact committed probe logic was independently reproduced in a clean Python environment: `7/7 PASS`.

## Red Team
The controls attack private-note leakage, private-score leakage, erased public status, erased public version, and undeclared output fields.

## Limits
The probe does not prove arbitrary non-inference for complex derived functions, adaptive side channels, authorization completeness, cryptographic privacy, or real private Genesis state. It is a bounded semantic model.

## Primitive reduction
No new primitive is justified. Projection/noninterference remains a constraint/behavior over State, Authority and Evidence rather than a `PrivacyBoundary`, `Projection`, `Redaction`, or `PublicState` primitive.

## Decision
Bounded noninterference is locally supported. Canonical promotion is not implied; hosted execution remains pending.

## Next discriminator
Use nested heterogeneous private/public state and derived public fields, with authorization contexts and an adversarial projection that attempts to leak a private field through a derived value. The test should be designed so the verifier catches the bad projection rather than merely asserting the intended implementation.
