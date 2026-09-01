# P212 — Competing Objectives / Hierarchical Trade-off Reduction

## Status
`SUPPORTED / HOSTED-VERIFIED / NOT CANONICAL`

## Purpose and bounded question

After P208 (constructive action classes), P209 (decision/selection/policy/preference), and P210 (plan/workflow/strategy/sequencing/replanning), this pass tests a materially different higher-order boundary: competing objectives, hierarchical priorities, trade-offs, equal-priority ambiguity, and objective mutation.

Question:

> Can the required semantics be reconstructed with `State + Transition + Capability + Authority + Observation + Evidence + Constraint`, without introducing `Objective`, `Goal`, `Tradeoff`, `Utility`, `Planner`, or an equivalent Genesis semantic primitive?

This is a clean-room probe. It does not import Genesis runtime code and does not treat implementation mechanisms as semantic evidence.

## Minimal contract

- Objective/priority data is represented as State.
- A candidate change is admissible only when Capability, Authority and Constraint permit it.
- Selection is a Transition-level choice, not a new primitive.
- Changing objective priorities is a State-changing Transition.
- Equal-ranked incompatible candidates remain ambiguous; the model must not invent authority.
- Observation and Evidence may inform state but do not silently create authority or mutate objectives.
- A material trade-off can fail closed when required authority is absent.

## Red Team / falsifiers

Attacks:

1. objective-as-primitive inflation;
2. goal/tradeoff/utility/planner inflation;
3. capability → authority laundering;
4. score → authority laundering;
5. Constraint bypass through a higher score;
6. objective mutation without a State transition;
7. equal-priority conflict silently resolved as success;
8. UNKNOWN observation granting objective-change authority;
9. Evidence silently mutating normative objectives;
10. missing material-change authority failing open;
11. legacy/runtime dependence;
12. CI PASS being confused with Genesis semantic correctness.

The first draft contained a reporting defect: 13 assertions were implemented while the printed count said 12. Red Team caught it. The closure probe was corrected to report 13, and only the corrected version is evidence.

A falsifier is a bounded objective/goal/trade-off case whose required invariant cannot be represented by the seven-element composition without an irreducible semantic distinction, authority boundary, or safety property.

## Local verification

The corrected committed probe was independently reproduced in a clean Python environment: `13/13 PASS`.

The probe reports `basis_size=7` and `new_primitive_required=false`.

## Hosted verification

Hosted execution is **verified**.

- workflow: `Objective Tradeoff Reduction`
- run ID: `33541107276`
- run number: `7`
- job ID: `99967278359`
- job conclusion: `success`
- hosted checkout SHA (`GITHUB_SHA`): `6a5dc1301d6ec49b73ebe83b3bc59065f8e7200e`
- pull-request source SHA: `14d907445307bd11b94c4e6aebe6091e4f66e457`
- exact checkout verification: `GITHUB_SHA == git rev-parse HEAD`
- probe result: `13/13 PASS`
- artifact: `p212-execution-evidence-6a5dc1301d6ec49b73ebe83b3bc59065f8e7200e`
- artifact ID: `9813623889`
- artifact digest: `sha256:7e0120b6c495628bf589ebc0e8a85007f6d6e2efd609c003898ab06ae53d6c4b`
- artifact state: `expired=false`

The hosted workflow ran on the pull-request merge ref, so the exact hosted execution SHA is the merge SHA `6a5dc130...`, not the source branch SHA. The merge commit was fetched and verified; its only change relative to its base is the hosted-verification comment, while the P212 probe and workflow were already present from the source SHA. The hosted log directly records the checkout SHA, all 13 PASS lines, `basis_size=7`, `new_primitive_required=false`, artifact finalization and the artifact digest.

The downloaded artifact ZIP was independently fetched and SHA-256 verified against the GitHub artifact digest; its payload contains the exact 13-PASS probe result.

## Cumulative interpretation

P208, P209 and P210 are reused as prior evidence that action classes, decision/selection, policy/preference and adaptive planning did not require new primitives. P212 adds a new discriminator: the normative ordering among multiple simultaneously relevant objectives.

Bounded result:

- Objective / Goal → State describing desired/preferred conditions;
- Priority / Trade-off → ordered State + Constraint composition;
- Objective mutation → Transition;
- Selection → transition choice bounded by Capability / Authority / Constraint;
- Ambiguity → observation/evidence/authority boundary, not a new primitive;
- Planner / Utility → implementation mechanism, not a Genesis semantic primitive.

Therefore P212 provides bounded supporting evidence against primitive inflation. It does **not** prove global ontology completeness, final minimality, universal multi-objective optimization correctness, or canonical Genesis semantics.

## Privacy boundary

This public probe contains only synthetic clean-room values. No private Genesis semantic state, private corpus, authority material, or witness material is included.

## Closure

`P212 = SUPPORTED / HOSTED-VERIFIED / NO NEW PRIMITIVE / NOT CANONICAL`
