# Primitive removal experiment

## Scope

Clean-room, Genesis-agnostic experiment following the concurrency/idempotency pass.

Question: can the semantic guarantee established there be represented without introducing a named `Idempotency` primitive?

## Reduction

The named concept is removed entirely from the semantic model. The experiment uses only:

- request identity;
- state;
- transition/application operation;
- an ordinary effect-cardinality constraint.

The constraint is:

`max_effects_per_request = 1`.

A counterfactual removes that constraint entirely.

## Executable result

With the ordinary constraint:

- final value = `v1`;
- effect count = `1`;
- repeated request identity is retained once.

Without the effect-cardinality constraint:

- final value = `v1`;
- effect count = `2`;
- the same request identity is applied twice.

Therefore the named concept is not required to preserve the tested guarantee. The **guarantee itself is required** when the contract demands at-most-one effect.

## Reduction verdict

`Idempotency as named primitive: REMOVE / NOT DEMONSTRATED`

`At-most-once effect: KEEP as contract/constraint when required`

This is an important distinction. Removing a name/primitive does not mean removing the underlying semantic requirement.

## What remains open

The model is deterministic and local. It does not prove that a generic constraint can be enforced in arbitrary distributed or physical systems, nor that the working Genesis basis is globally complete. Crash windows, persistence, partitions, authority races and external effect verification remain open.

## Epistemic status

`OBSERVED / BOUNDED EXPERIMENT`.

## Public boundary

No Genesis source, private architecture, canonical decision, credentials, internal endpoints or private datasets are present. Canonical interpretation remains in `genesis-lab`.
