# P198 — Temporal publication authority

## Question
Does authority valid at derivation time remain sufficient for publication after time, revocation, or contract drift?

## Non-duplication
P191 covers ambiguity-aware governed action. P194 covers projection collision requiring revalidation. P197 covers declared and authorized private→public derivation. P198 is distinct: it tests the temporal boundary between derivation/admission and publication.

## Hypothesis
Publication authorization is a transition condition evaluated at publication time, not a durable fact cached from derivation time.

## Bounded test
`temporal_publication_authority.py` exercises fresh authority, expiry, exact expiry boundary, revocation, contract drift, refreshed authority, stale authority, and cached-admission bypass.

## Local result
Expected: `TEMPORAL PUBLICATION AUTHORITY: 8/8 PASS`.

## Red Team
- cached admission after revocation must not authorize publication;
- unexpired authority with changed contract must not publish;
- expired authority must not publish;
- exact boundary is governed explicitly rather than implicitly;
- refreshed authority must be bound to the current contract.

## Primitive reduction
No new Genesis primitive is justified by this bounded result. The behavior composes authority, time, contract/state, and transition.

## Epistemic status
LOCAL_TEST_DEFINED_PENDING_HOSTED_CI

Hosted CI must be verified against the exact commit before canonical promotion.
