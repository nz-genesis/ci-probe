# P213 — Partial-order / Incomparable Normative Trade-off Reduction

## Status
`EXPERIMENTAL / LOCAL PASS / HOSTED-CI PENDING / NOT CANONICAL`

## Purpose and new discriminator
P212 tested weighted/hierarchical objective ordering. P213 deliberately changes the discriminator: objectives can be genuinely incomparable, a partial precedence relation can later make one objective dominant, and the unresolved set can resemble a Pareto frontier.

Question:

> Does partial-order/incomparable normative structure require a new Genesis semantic primitive beyond `State + Transition + Capability + Authority + Observation + Evidence + Constraint`?

This is a clean-room probe and does not import Genesis runtime code.

## Minimal contract

- The objective precedence relation is State.
- Incomparable top-level objectives remain incomparable; the system must not silently manufacture an order.
- Adding/removing precedence is a State-changing Transition.
- Capability, Authority and Constraint continue to bound admissibility.
- Evidence and Observation do not silently create normative precedence.
- A human or other explicit authority may be represented as a Constraint/Authority boundary for tie-breaking; this is not itself a new Genesis primitive.
- Pareto/frontier-like sets are derived State/Observation, not a primitive.

## Red Team / correction genealogy

The first P213 implementation contained two defects caught before closure:

1. it printed `assertions=12` while implementing 13 checks;
2. its first dominance implementation ignored the precedence relation, so the claimed state-relation mutation did not actually change the frontier.

Both defects were rejected as evidence. The implementation was corrected so `objective_order` is an explicit State relation and only top-level incomparable objectives participate in the bounded dominance test. The corrected local reproduction produced `13/13 PASS`.

Attacks:

- partial-order primitive inflation;
- Pareto/frontier primitive inflation;
- objective/goal/trade-off/utility/planner inflation;
- authority laundering;
- capability laundering;
- Constraint bypass;
- silent ordering of incomparable objectives;
- objective relation mutation without State transition;
- Evidence-created precedence;
- UNKNOWN-created precedence;
- missing explicit tie-break authority;
- implementation/runtime dependence.

A falsifier is a bounded case where an irreducible normative relation, authority boundary, or safety invariant cannot be represented through the seven-element composition.

## Local verification

Corrected committed probe: `partial_order_normative_reduction.py`.

Independent clean-environment reproduction: `13/13 PASS`.

## Hosted verification boundary

Dedicated workflow:
`.github/workflows/partial-order-normative-reduction.yml`

Hosted PASS is not claimed until exact run/SHA/job/log/artifact evidence is fetched and verified.

Required chain:
`checkout github.sha → verify git rev-parse HEAD == GITHUB_SHA → execute → fetch run → fetch job/logs → fetch artifact → verify artifact digest`.

## Cumulative interpretation

P208–P212 remain prior evidence. P213 adds a new discriminator rather than repeating weighted decision or planning tests. Even a successful P213 run would be bounded evidence against primitive inflation, not proof of global completeness or final minimality.

## Privacy boundary

Synthetic clean-room values only. No private Genesis semantic state, authority corpus, witness material, or private correspondence data is exposed.
