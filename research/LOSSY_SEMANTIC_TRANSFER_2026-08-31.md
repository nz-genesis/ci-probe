# P193 — Lossy Semantic Transfer

Date: 2026-08-31
Status: bounded executable evidence; hosted CI must be checked separately.

## Question
Can a cross-domain transformation that loses decision-relevant semantic information create a false unique interpretation?

## Non-duplication
P190 covered exact cross-domain consumption and deterministic semantic translation. P192 covered preservation of unresolved alternatives across a domain boundary. P193 isolates a new discriminator: the target representation may look unique after information loss even though the source contained multiple materially different candidates.

## Acceptance boundary
A consumer MUST NOT infer semantic uniqueness from a reduced representation when decision-relevant information was lost. If the action is safe for every source candidate, safe consumption remains possible. A validated observation may restore a unique interpretation. Confidence or target-side uniqueness alone is insufficient.

## Executable
`lossy_semantic_transfer.py`

## Cases
1. lossless unique -> CONSUME
2. lossy collapse creating false uniqueness -> UNRESOLVED
3. lossy but action invariant for all source candidates -> SAFE_CONSUME
4. irrelevant information loss with a single source candidate -> CONSUME
5. forged unique target from multiple source candidates without validated observation -> UNRESOLVED
6. validated observation restores distinction -> CONSUME
7. lossy multiple targets with universally safe action -> SAFE_CONSUME
8. lossless unique unauthorized -> UNAUTHORIZED

## Local verification
Exact committed executable content was reproduced and executed locally: `LOSSY SEMANTIC TRANSFER: 8/8 PASS`.

## Red Team
- Target uniqueness can be a projection artifact.
- Authority cannot delete an alternative merely because it is inconvenient.
- Reversibility does not imply semantic safety for all source candidates.
- Information loss is not automatically harmful when it is decision-irrelevant or the action is invariant across all candidates.
- A validated observation may legitimately remove ambiguity.

## Primitive reduction
No new Genesis primitive is justified. The behavior composes source state, target representation, evidence/observation, constraints, authority, capability and transition/consumption semantics.

## Negative boundary
This does NOT establish universal information-loss detection, semantic equivalence in arbitrary domains, or physical-world truth.

## CI
Workflow: `.github/workflows/lossy-semantic-transfer.yml`.
Hosted CI status is intentionally not asserted until a completed run for the current main SHA is independently inspected.
