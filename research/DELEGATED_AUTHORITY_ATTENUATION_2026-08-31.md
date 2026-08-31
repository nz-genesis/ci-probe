# P199 — Delegated authority attenuation

## Question
Can a delegated authority be accepted as valid only when it is no broader than its parent along action, resource, temporal, and risk dimensions?

## Non-duplication
The existing multi-hop revocation/HITL evidence verifies parent-lineage validity and revocation behavior, but explicitly leaves delegated authority attenuation rules beyond simple parent-validity intersection open. P199 targets that stated gap.

## Hypothesis
Delegation is safe only when each child authority is monotonically no broader than its parent; escalation in any governed dimension must be rejected.

## Bounded test
`delegated_authority_attenuation.py` tests action scope, resource scope, expiry, risk limit, equal scope, multi-dimensional narrowing, and single-dimension escalation.

## Local result
`DELEGATED AUTHORITY ATTENUATION: 8/8 PASS`.

## Red Team
The principal attack is authority laundering through one widened dimension while all other dimensions remain narrower. Any single-dimension escalation must invalidate the child authority.

## Primitive reduction
No new Genesis primitive is justified. The bounded rule composes authority, constraint, scope, time, and risk attributes.

## Epistemic status
LOCAL_PASS_PENDING_HOSTED_CI

## Canonical impact
None. This is bounded verification evidence; it does not alter Purpose, Constitution, Core Model, or primitive set.
