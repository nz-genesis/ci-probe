# P200 — Semantic Effective Authority Composition

Date: 2026-08-31
Status: `LOCAL_VERIFIED / HOSTED_CI_PENDING / NON-CANONICAL`

## Question
Does multi-hop delegation remain monotone when authority is evaluated by semantic effect rather than by the syntax of the immediately preceding authority record?

## Non-duplication
P199 tests component-wise single-hop attenuation. Existing `dynamic_delegation.py` tests whole-chain validity/revalidation at realization. P200 is narrower and distinct: it tests semantic effect composition, including alias normalization, nearest-parent laundering, sibling non-union, and monotonicity of the effective effect set across hops.

## Method
Represent an authority by action scope, resource scope and risk bound. Normalize action aliases before comparison. Expand each authority into a finite semantic effect set `(canonical_action, resource, risk)`. A child delegation is valid only when its semantic effects are a subset of the effective ancestor authority. The effective chain is therefore computed as repeated subset-preserving composition; sibling authorities are never unioned.

## Cases
1. valid A→B→C attenuation;
2. leaf effects remain within root effects;
3. action escalation;
4. resource escalation;
5. risk escalation;
6. semantic alias escalation;
7. nearest-parent laundering where an intermediate node already widened authority;
8. sibling union confusion;
9. monotonic effective-set chain;
10. empty authority remains empty.

## Result
Local execution of the exact committed executable: `SEMANTIC EFFECTIVE AUTHORITY COMPOSITION: 10/10 PASS`.

## Red Team
Attacks considered: frame/semantic alias switching, single-dimension widening, nearest-parent validation, sibling union, and hidden widening behind representation. All are rejected by the bounded model.

## Finding
For this finite model, delegation must be monotone with respect to semantic effect, not merely syntactic authority fields or immediate-parent validity. The effective authority of a descendant cannot exceed the effective authority of any ancestor.

## Primitive reduction
No new Genesis primitive is justified by this bounded result. The behavior composes existing notions of authority, scope, constraints and transition.

## Limitations
The probe does not establish a universal authority algebra. It omits richer effects, contextual policies, obligations, resource identity resolution, temporal intervals, capabilities, and real Genesis runtime integration. Hosted CI remains pending and canonical promotion is not performed.

## Next bounded question
Test whether semantic effect monotonicity remains valid when delegation crosses a change of authority schema/representation, including explicit schema-version compatibility and rejection of incomparable semantics.
