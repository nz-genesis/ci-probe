# P203 — Evidence-Bound Compatibility Scope

Date: 2026-08-31
Status: BOUNDED / LOCAL VERIFIED; HOSTED CI PENDING AT WRITE TIME

## Question

Can compatibility evidence validly authorize a conversion outside the semantic scope for which that evidence was established?

## Non-duplication

P199/P200 address authority attenuation/composition across delegation. P201 addresses semantic schema compatibility. P202 establishes that a compatibility claim is not itself proof. P203 is narrower: whether otherwise-valid compatibility evidence can be reused when required decision scope changes.

## Method

Evidence is represented with explicit schema, resource, action, policy, and version scope. A decision accepts only when the evidence scope covers every required scope dimension. Missing or mismatched dimensions reject closed.

## Cases

1. exact scope — ACCEPT
2. resource change — REJECT
3. action change — REJECT
4. policy change — REJECT
5. version change — REJECT
6. schema change — REJECT
7. missing evidence scope — REJECT
8. extra evidence metadata while required scope remains covered — ACCEPT
9. stripped resource/action scope — REJECT
10. read evidence reused for write — REJECT

## Local result

`EVIDENCE SCOPE BINDING: 10/10 PASS`

## Red Team

The decisive attacks are scope stripping, action widening, resource substitution, policy/version drift, and reuse of read-scoped evidence for write. All are rejected.

## Finding

Compatibility evidence must be bound to the semantic decision scope. Validity of evidence in one scope does not imply validity in another. Scope mismatch must fail closed or trigger fresh verification.

## Primitive reduction

No new Genesis primitive is justified by this bounded result. The behavior can be represented through existing Evidence, Scope, Authority, Constraint, State, Verification, and Transition semantics.

## Limitations

The probe uses exact equality for scope dimensions. It does not yet establish richer subset/containment semantics, time intervals, hierarchical resources, or compositional policy implication.

## Hosted verification

The workflow was created for the committed executable. Hosted status must be independently re-fetched for the exact resulting commit before reporting CI success, per `GITHUB_WRITE_VERIFICATION_RULE.md`.
