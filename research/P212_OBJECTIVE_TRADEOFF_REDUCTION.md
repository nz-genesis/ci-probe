# P212 — Competing Objectives / Hierarchical Trade-off Reduction

## Status
`EXPERIMENTAL / HOSTED-CI PENDING / NOT CANONICAL`

## Purpose and bounded question

After P208 (constructive action classes), P209 (decision/selection/policy/preference), and P210 (plan/workflow/strategy/sequencing/replanning), this pass tests a materially different higher-order boundary: competing objectives, hierarchical priorities, trade-offs, and objective mutation.

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

A falsifier is a bounded objective/goal/trade-off case whose required invariant cannot be represented by the seven-element composition without an irreducible semantic distinction, authority boundary, or safety property.

## Local verification

The committed probe was fetched at commit `01c4b890589629b441204a72a21df000f03642b7` and independently reproduced in a clean Python execution environment: `13/13 PASS`.

The probe reports `basis_size=7` and `new_primitive_required=false`.

## Hosted verification

The dedicated workflow is designed to verify:

`checkout github.sha → verify git rev-parse HEAD == GITHUB_SHA → execute → upload execution evidence`.

Hosted PASS is intentionally not claimed until the run, exact SHA, job logs and artifact are independently fetched and verified.

## Cumulative interpretation

P208, P209 and P210 are reused as prior evidence that action classes, decision/selection, policy/preference and adaptive planning did not require new primitives. P212 adds a new discriminator: the normative ordering among multiple simultaneously relevant objectives.

A successful P212 probe would be bounded evidence against primitive inflation, not proof of global ontology completeness or final minimality.

## Privacy boundary

This public probe contains only synthetic clean-room values. No private Genesis semantic state, private corpus, authority material, or witness material is included.
