# P191 — Ambiguity → Governed Action

Date: 2026-08-31
Status: bounded executable probe; canonical Genesis promotion NOT claimed.

## Question
Can ambiguity be preserved as an explicit unresolved state while action governance distinguishes interpretation confidence from authority, reversibility, and availability of discriminating observation?

## Discriminator
The probe exercises eight cases: unique authorized interpretation; ambiguous reversible action; ambiguous irreversible action; observation-first; HITL; high-confidence-but-ambiguous action; no authorized interpretation; and a second high-confidence ambiguity case.

## Result
`AMBIGUITY GOVERNED ACTION: 8/8 PASS` is the expected exact executable output for the committed probe.

## Interpretation
The bounded composition does not require an `AmbiguityPrimitive`, `DecisionEngine`, or `InterpretationResolver`. Ambiguity can remain represented as candidate state while authority and action properties constrain transitions.

Critical distinction: confidence is evidence about an interpretation; it is not itself authority to execute an irreversible action.

## Red Team
Attack: choose the highest-confidence candidate whenever confidence is high. Counterexample: two authorized interpretations with materially different irreversible actions. The probe requires `NO_EXECUTION` rather than collapsing ambiguity.

Attack: treat reversibility as authorization. Counterexample: ambiguous reversible action with no unique authorized interpretation. The bounded policy remains `HOLD_OR_SAFE_REVERSIBLE` rather than asserting authority.

Attack: treat observation as execution authority. Counterexample: observation availability causes `OBSERVE_FIRST`, not immediate irreversible execution.

## Reduction
No new Genesis primitive is justified. Reuse/composition of state, evidence, authority, capability/constraint, observation and transition semantics is sufficient for this bounded question.

## Limits
This does not prove universal decision safety, calibrated probabilistic semantics, real-world HITL behavior, or canonical Genesis readiness. Hosted CI completion must be checked separately from local executable semantics.

## Genealogy
Builds on prior semantic translation, authority/HITL, observation, and irreversibility work but uses a distinct discriminator: action governance under unresolved semantic alternatives.
