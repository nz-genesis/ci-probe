# Distributed Replay Race — 2026-08-30

## Status
BOUNDED NEGATIVE RESULT / LIMIT CONFIRMED.

## Question
Does verifier-local replay state provide distributed replay protection when two independent verifiers consume the same semantic receipt concurrently?

## Prior evidence
The provenance/replay probe established bounded protection for replay and substitution when consumption state is shared by one verifier. This experiment is deliberately not a repetition: it removes shared consumption state and introduces two independent verifiers.

## Model
A receipt is represented only by generic fields: commitment, nonce, realizer, effect. Each verifier maintains its own consumed set. No Genesis-specific primitive or semantic label is introduced.

## Result
The same receipt is rejected on a second attempt by verifier A, but accepted by independent verifier B. Therefore verifier-local freshness state is insufficient for distributed replay protection.

## Interpretation
This is evidence about a distributed coordination boundary, not evidence that a new Genesis primitive is required. The result can be represented as a state-consistency / authority / provenance constraint. Whether that representation is minimal or canonical remains open.

## Red Team / omission gate
- Does this merely repeat the prior replay test? No: the discriminator is independent consumption state.
- Does a renamed field create a primitive? No.
- Does local replay rejection imply global replay rejection? No; counterexample demonstrated.
- Does this establish a Genesis Execution/Verifier primitive? No.
- Remaining discriminator: concurrent atomic claim/consumption under a shared trust domain, then cross-domain trust-root equivocation.

## Canonical impact
Global Purpose: unchanged.
Genesis ontology: unchanged.
New primitives: 0.
P190: not started.
