# External Effect + Independent Observation — 2026-08-31

**Status:** EXPERIMENTAL / EXECUTABLE / LOCAL PASS / HOSTED-CI PENDING

## Question
Does Genesis need to distinguish execution acknowledgement from independently observed external-world effect?

## Non-duplication
Existing repository research covers in-flight irreversible effects, atomic consumption and recovery races. This pass adds a distinct discriminator: the authoritative observation comes from a world model independent of executor acknowledgement.

## Model
The bounded external world stores observable `effect_id` values. An executor returns an acknowledgement separately. An independent observer reads the world directly. Re-execution uses the same effect identity in an idempotent bounded world model.

## Local result
The exact committed probe logic was independently reproduced in a clean Python environment:

`EXTERNAL EFFECT INDEPENDENT OBSERVATION: 6/6 PASS`

## Red Team
- timeout-after-effect: world observation succeeds even when acknowledgement is false;
- acknowledgement-without-effect: acknowledgement alone does not prove world change;
- same effect identity on retry does not add a second observable effect in the bounded idempotent world;
- distinct effect identity remains distinguishable.

## Semantic result
The tested distinction is real: `execution acknowledgement != independently observed world consequence`.

No new Genesis primitive is justified. The distinction is representable through existing candidate composition of Execution/Transition/Effect + Observation + Evidence + Verification + Lineage/State. An `ExternalWorld` or `WorldObserver` primitive is not introduced.

## Limits
The probe does not prove real external idempotency, exactly-once semantics across arbitrary providers, physical-world truth, network reliability, or independent observer authenticity. It is a bounded semantic model.

## Decision
Bounded external-observation distinction is locally supported. Canonical promotion is not implied; hosted CI remains pending.

## Next discriminator
Test a non-idempotent external effect where executor timeout occurs after the effect but before acknowledgement, and compare recovery policies with and without an independently queryable effect identity. The test should expose the impossibility boundary rather than assume idempotency.
