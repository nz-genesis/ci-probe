# Private→Public Semantic Correspondence — 2026-08-30

## Purpose

Bounded clean-room harness for the unresolved P189 external-realization correspondence question. The harness uses a generic private semantic surrogate, not a real private Genesis semantic vector. Therefore it can validate the correspondence mechanism and Red-Team properties, but cannot close the canonical private→public correspondence gate.

## Non-duplication

This is not another coordinator, replay, recovery, stale-read, or authority-race experiment. Prior archaeology established that authority/history semantics already exist in Genesis composition. The remaining question is whether materially relevant private dimensions can cross a public realization boundary as opaque, independently verifiable evidence without disclosure or semantic loss.

## Model

Private vector contains generic dimensions:

```text
operation
authority
lineage
temporal
verification
external-effect contract
private-only annotation
```

Public projection contains only opaque commitments/identifiers derived from those dimensions. The private-only annotation is intentionally excluded because it is declared irrelevant to the bounded realization semantics.

## Local executable result

The exact harness was independently executed from the repository artifact in a local Python runtime on 2026-08-30:

```text
10/10 PASS
```

All ten assertions passed: baseline correspondence, opaque public schema, irrelevant annotation exclusion, mutation detection for authority/lineage/temporal/verification/effect/operation, and public-key/private-key separation.

This is local execution evidence only. The container could not reach GitHub directly, so no local network execution is being represented as hosted CI evidence.

## Acceptance properties

1. baseline private/public correspondence verifies;
2. public projection contains no raw private values;
3. changing an irrelevant private annotation does not change the projection;
4. changing any material semantic dimension invalidates correspondence;
5. operation substitution invalidates correspondence;
6. public projection alone cannot reconstruct the private fields in the harness model.

## Red Team

The principal attacks are mutation sensitivity, authority laundering, oracle leakage, reconstruction, and accidental inclusion of private-only fields. The harness explicitly checks all of these bounded properties.

The strongest Red-Team limitation is also explicit: commitments prove binding only relative to the test construction; they do not by themselves prove semantic equivalence, real private-state provenance, or resistance to every cryptographic/adaptive attack.

## Epistemic boundary

The local PASS establishes only that this generic commitment-envelope mechanism has the desired bounded correspondence properties. It does **not** establish that a real Genesis semantic vector can be safely projected, because the fixture is not private Genesis state and the cryptographic construction is a test mechanism rather than a Genesis primitive.

The canonical decisive test remains: a real private semantic vector must be used privately, a non-revealing projection derived, public realization executed, and the result verified privately against the original vector.

## Primitive reduction

No new Genesis primitive is introduced. Commitments, envelopes, hashes, HMACs and projection records are external realization mechanisms.

## Status

`BOUNDED / LOCAL PASS 10/10 / HOSTED-CI PENDING / NOT CANONICAL`

`PRIVATE→PUBLIC GENESIS CORRESPONDENCE = STILL UNRESOLVED`
