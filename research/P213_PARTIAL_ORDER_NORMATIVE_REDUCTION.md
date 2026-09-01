# P213 — Partial-order / Incomparable Normative Trade-off Reduction

## Status
`SUPPORTED / HOSTED-VERIFIED / NOT CANONICAL`

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

Two substantive defects were caught before closure:

1. the first implementation printed `assertions=12` while implementing 13 checks;
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

No Red-Team attack produced a falsifying semantic residue in the corrected bounded model.

## Local verification

Corrected committed probe: `partial_order_normative_reduction.py`.

Independent clean-environment reproduction: `13/13 PASS`.

## Hosted verification — independently fetched and verified

- workflow: `Partial Order Normative Reduction`
- run ID: `33541734173`
- run number: `3`
- job ID: `99969387904`
- conclusion: `success`
- pull-request source SHA: `21ce8d22fc668153cc759db28be7b7ae2b2fd9be`
- exact hosted `GITHUB_SHA`: `24dd0ac3f52130c85d832ed7daaa5660034f6e32`
- exact checkout: `git rev-parse HEAD == GITHUB_SHA`
- probe: `13/13 PASS`
- basis size: `7`
- new primitive required: `false`

The workflow ran against the pull-request merge ref. The hosted log records checkout of merge SHA `24dd0ac3...`, the exact SHA identity check, all 13 PASS lines, and artifact finalization. The fetched merge commit was independently verified; the merge contains the P213 workflow, corrected probe and public research record from the source SHA.

Execution artifact:

- name: `p213-execution-evidence-24dd0ac3f52130c85d832ed7daaa5660034f6e32`
- artifact ID: `9813869742`
- size: `462` bytes
- expired: `false`
- GitHub digest: `sha256:c0040242334ebb82a4af4f8ba7c3f3f4ec9808b68b4a98d167fbe57f173befb6`

The artifact ZIP was downloaded and its SHA-256 independently recomputed to the same GitHub-reported digest. Its payload contains the exact 13-PASS result.

## Semantic result

The bounded evidence supports reduction:

- partial objective precedence → State relation;
- incomparable objectives → unresolved State/Observation/Evidence boundary rather than invented ordering;
- precedence mutation → Transition;
- admissibility → Capability + Authority + Constraint;
- frontier/Pareto-like set → derived State/Observation;
- tie-break → explicit Authority/Constraint composition;
- planner/utility → implementation mechanism.

Therefore P213 provides bounded supporting evidence against primitive inflation. It does **not** prove universal normative reasoning, global ontology completeness, final minimality, or canonical Genesis semantics.

## Privacy boundary

Synthetic clean-room values only. No private Genesis semantic state, authority corpus, witness material, or private correspondence data is exposed.

## Closure
`P213 = SUPPORTED / HOSTED-VERIFIED / NO NEW PRIMITIVE / NOT CANONICAL`
