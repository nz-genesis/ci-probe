# P201 — Authority Schema Compatibility

Date: 2026-08-31
Status: `LOCAL_VERIFIED / HOSTED_CI_PENDING / NON-CANONICAL`

## Question
When delegated authority crosses a schema/representation boundary, can a conversion be accepted safely without proving semantic compatibility?

## Non-duplication
Archaeology searched `ci-probe` and `genesis-lab` for schema compatibility, representation compatibility, authority conversion, and delegation compatibility. No existing bounded probe was found that classifies cross-schema authority conversion as equivalent, attenuating, widened, or incomparable and fails closed on unknown schema semantics. P199 covers component-wise single-hop attenuation; P200 covers semantic effect composition within one authority representation. P201 targets the representation/schema boundary itself.

## Method
Represent authority by action scope, resource scope, and risk bound. Expand each representation into a finite semantic effect set `(action, resource, risk)`. If schemas are explicitly compatible, classify target effects relative to source effects as `EQUIVALENT`, `ATTENUATED`, `WIDENED`, or `INCOMPARABLE`. If schema compatibility is not established, classify as `INCOMPARABLE` regardless of apparent equality of known fields. Governed conversion accepts only equivalent or attenuated results; widened and incomparable results are rejected.

## Cases
1. equivalent compatible conversion;
2. attenuated compatible conversion;
3. action widening;
4. resource widening;
5. risk widening;
6. disjoint/incomparable semantics;
7. incompatible schema despite equal records;
8. unknown/new semantics under an incompatible schema.

## Local verification
The exact committed executable was copied from the repository state into an isolated local execution environment and produced: `AUTHORITY SCHEMA COMPATIBILITY: 8/8 PASS`.

## Red Team
Attacks: hidden action widening, resource widening, risk widening, disjoint semantics forced into an ordering, schema incompatibility masked by equal known fields, and unknown target semantics accepted because known fields appear narrower. All fail closed in the bounded model.

## Finding
Structural conversion is not sufficient evidence of semantic compatibility. A schema boundary must have explicit compatibility evidence. Unknown or incomparable semantics must not be silently treated as equivalent or attenuated for governed action.

## Primitive reduction
No new Genesis primitive is justified. The bounded result composes existing authority, scope, constraints, representation, evidence, and transition semantics.

## Limitations
This is a finite model. It does not establish a universal schema-compatibility algebra, cover arbitrary policy languages, prove resource identity equivalence, or test a real Genesis runtime. Hosted CI is pending; canonical promotion is not performed.

## Next bounded question
Test compatibility when a schema conversion is explicitly declared compatible but its semantics are changed by defaults, enum expansion, omitted fields, units, or policy-version changes; determine whether compatibility must be field-level, effect-level, or contract-level.
