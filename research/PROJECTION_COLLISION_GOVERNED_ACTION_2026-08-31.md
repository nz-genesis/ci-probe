# P194 — Projection Collision Governed Action

Date: 2026-08-31
Status: bounded executable evidence; hosted CI must be checked separately.

## Relation to prior evidence
The 2026-08-30 clean-room projection mutation test already established a representational negative result: private-only changes to authority, resource version, temporal constraint and verification can leave the public projection unchanged. P194 does not repeat that mutation test. It asks the downstream safety question: what must a projection-only consumer do when such a collision exists?

## Question
Can a projection-only consumer safely execute an action when decision-relevant private state is not represented in the public projection?

## Acceptance boundary
A projection collision must not be interpreted as semantic equivalence. Projection-only consumption requires revalidation. A full-state consumer may distinguish the actual authority, freshness, temporal and verification outcomes.

## Cases
- baseline full state -> EXECUTE; projection-only -> REQUIRE_REVALIDATION
- authority revoked with identical projection -> UNAUTHORIZED; projection-only -> REQUIRE_REVALIDATION
- resource version changed -> STALE; projection-only -> REQUIRE_REVALIDATION
- temporal constraint changed -> OUTSIDE_WINDOW; projection-only -> REQUIRE_REVALIDATION
- verification condition changed -> UNVERIFIED; projection-only -> REQUIRE_REVALIDATION

## Local verification
Exact executable reproduced and executed: `PROJECTION COLLISION GOVERNED ACTION: 10/10 PASS`.

## Red Team
The dangerous failure is not a projection mismatch. It is a projection collision: the public representation remains equal while private decision-relevant state changes. The safe response is revalidation, not inferred equivalence.

## Primitive reduction
No new Genesis primitive is justified. The result composes representation/projection, state, authority, freshness, constraints, verification and governed transition semantics.

## Boundary
This remains clean-room generic evidence. It does not expose or verify any private Genesis contract and does not prove universal projection correctness.
