# HITL boundary experiment

## Scope

Clean-room, Genesis-agnostic governance experiment. It tests only whether explicit authority, risk, and irreversibility boundaries can require a human decision without making `HITL` a standalone primitive.

This experiment does not measure human cognition, quality of human decisions, or real-world authority. It models the governance rule that a human decision is required at specified boundaries.

## Cases

| Case | Authority | Risk | Irreversible | Human decision required |
|---|---|---:|---:|---:|
| reversible-low-risk | clear | 2 | no | no |
| high-risk-reversible | clear | 9 | no | yes |
| irreversible-authorized | clear | 3 | yes | yes |
| ambiguous-authority | ambiguous | 2 | no | yes |
| unauthorized | absent | 2 | no | no; reject |

## Reduction

No named HITL primitive is used. The requirement is represented as an ordinary governance constraint:

`human_decision_required = authority_ambiguous OR irreversible OR risk >= threshold`.

Removing the constraint from the irreversible case changes the admissibility result from blocked-pending-human-decision to admitted. This demonstrates semantic loss from removing the **boundary rule**, not from removing a named HITL primitive.

## Observed result

The experiment supports:

- human involvement is not universally required;
- human decision can be required by a material authority/risk/irreversibility boundary;
- the boundary can be represented as a governance constraint;
- unauthorized proposals are rejected rather than automatically escalated to a human;
- no independent HITL primitive is required by this bounded model.

## Important limitation

The experiment does not prove that every real-world governance boundary can be reduced to these fields. It also does not prove that human intervention is sufficient for safety. Real authority systems, organizational delegation, emergency procedures, physical hazards, irreversible side effects, and human-factor failures require separate evidence.

## Epistemic status

`OBSERVED / BOUNDED EXPERIMENT`.

## Public boundary

No Genesis source, private architecture, credentials, datasets, internal endpoints, or canonical decisions are included. Interpretation remains in private `genesis-lab`.
