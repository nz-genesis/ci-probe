# P202 — Authority Compatibility Claim vs Semantic Compatibility

Date: 2026-08-31
Status: `LOCAL_VERIFIED / HOSTED_CI_PENDING / NON-CANONICAL`

## Question
Can an explicit compatibility claim safely authorize an authority schema conversion when actual semantics may change through defaults, enum expansion, omitted fields, units, or policy-version changes?

## Non-duplication
Archaeology searched `genesis-lab` and `ci-probe` for schema compatibility, representation compatibility, authority conversion, defaults, enum expansion, omitted fields, units, and policy-version compatibility. No existing bounded probe was found that tests whether a positive compatibility claim itself constitutes sufficient evidence under these semantic-drift mechanisms. P201 establishes that compatibility must be explicit; P202 tests whether the claim is sufficient evidence without validating the underlying semantic contract.

## Method
Model authority as actions, resources, risk bound, unit, and policy version. Require both an explicit compatibility claim and independent stability evidence for defaults, enum semantics, omission semantics, units, and policy semantics. A target is accepted only when the verified semantic effect set is a subset of the source effect set. Any failed stability evidence or absent claim causes rejection.

## Cases
1. claimed compatible + stable semantics + attenuation;
2. default semantic change;
3. enum expansion;
4. omitted-field semantic change;
5. unit change;
6. policy-version semantic change;
7. false compatibility claim masking widening;
8. no compatibility claim.

## Local verification
The exact committed executable produced: `AUTHORITY COMPATIBILITY CLAIM: 8/8 PASS`.

## Red Team
Attacks target the trust boundary around the compatibility claim: treating metadata as proof, hiding new effects behind defaults or enums, changing omission semantics, changing units, and changing policy semantics while retaining a positive compatibility label. All bounded attacks reject.

## Finding
A compatibility claim is an assertion, not semantic evidence. Governed conversion requires independently verified semantic compatibility and effect-level non-widening. Unknown semantic drift must fail closed.

## Primitive reduction
No new Genesis primitive is justified. The result composes existing authority, representation, constraints, evidence, state, and transition semantics.

## Limitations
Finite model only. It does not prove compatibility of arbitrary schema languages, parsers, serialization formats, units, policy DSLs, or a real Genesis runtime. Hosted CI and canonical promotion remain separate gates.

## Next bounded question
Determine whether semantic compatibility evidence itself requires provenance, freshness, authority, and revalidation before it can govern an execution-affecting conversion.
