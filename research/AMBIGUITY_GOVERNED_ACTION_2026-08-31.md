# P191 — Ambiguity → Governed Action

Date: 2026-08-31
Status: bounded executable probe; canonical Genesis promotion NOT claimed.

## Question
Can ambiguity be preserved as an explicit unresolved state while action governance distinguishes interpretation confidence from authority, reversibility, safety-under-all-candidates, and availability of discriminating observation?

## Discriminator
The corrected probe exercises nine cases: unique authorized interpretation; ambiguous reversible but not universally-safe action; ambiguous reversible action safe for all candidates; ambiguous irreversible action; observation-first; HITL; high-confidence-but-ambiguous action; unauthorized alternative preserving ambiguity; and a second high-confidence ambiguity case.

## Result
`AMBIGUITY GOVERNED ACTION: 9/9 PASS` on the corrected committed executable. The hosted run must be treated as the evidence-bearing execution only when its head SHA and job logs are independently verified.

## Critical correction
The earlier bounded model incorrectly allowed an ambiguous reversible action to return `HOLD_OR_SAFE_REVERSIBLE`, conflating two materially different outcomes. The corrected model permits `SAFE_REVERSIBLE` only when the action is explicitly safe for all remaining candidate interpretations. It also requires uniqueness of interpretation, not merely uniqueness of authorized candidates, before `EXECUTE`.

## Interpretation
The bounded composition does not require an `AmbiguityPrimitive`, `DecisionEngine`, or `InterpretationResolver`. Ambiguity remains candidate state; authority does not collapse semantic uncertainty; reversibility does not create authority; and a reversible action is safe only when its safety is invariant across the unresolved candidate set.

## Red Team
Attack: choose the highest-confidence candidate whenever confidence is high. Counterexample: two authorized interpretations with materially different irreversible actions. Required result: `NO_EXECUTION`.

Attack: let an unauthorized alternative disappear from the candidate set. Counterexample: one authorized and one unauthorized interpretation. Required result: `NO_EXECUTION`, because authorization is not truth.

Attack: treat reversibility as sufficient for execution. Counterexample: ambiguous reversible action not safe for all candidates. Required result: `NO_EXECUTION`.

Attack: treat observation as execution authority. Required result: `OBSERVE_FIRST`.

## Reduction
No new Genesis primitive is justified. The bounded semantics remain expressible through candidate state, evidence, authority, constraints/capability, observation and transition semantics.

## Limits
This does not prove universal decision safety, calibrated probabilistic semantics, real-world HITL behavior, arbitrary multi-agent ambiguity resolution, or canonical Genesis readiness. Hosted CI completion and exact SHA must be checked separately from local executable semantics.

## Genealogy
Builds on prior semantic translation, authority/HITL, observation, irreversibility and P191 work but uses a distinct discriminator: whether governance accidentally converts authority, confidence, or reversibility into semantic truth.
