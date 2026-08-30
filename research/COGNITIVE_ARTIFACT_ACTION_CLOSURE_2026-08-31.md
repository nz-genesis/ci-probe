# Bounded Cognitive / Artifact Action Closure — 2026-08-31

## Status
EXPERIMENTAL / EXECUTABLE / HOSTED-CI PENDING

## Question
Can a cognitive capability be represented as a governed executable operation producing a provenance-bearing, minimally verifiable artifact without requiring a specific LLM or cognition implementation as a Genesis Base primitive?

## Prior-art boundary
This pass follows the repository's Action Closure / Toaster research and the cognitive archaeology record. It does not repeat environment-only symmetry, replay, ACK, coordinator, partition, or divergent-authority tests.

## Bounded model
Contract fields:
- operation_id
- intent
- capability
- authority
- input_root
- engine
- seed
- version

The engine is an implementation parameter. A deterministic hash-based surrogate stands in for cognition; no claim is made about real LLM factuality or semantic quality.

Path:

`intent/context -> cognitive capability -> executable synthesis -> artifact -> provenance -> verification`

## Tests
1. baseline synthesis and verification
2. exact replay with same envelope
3. replaceable cognition engine with same contract shape
4. changed input root changes artifact and provenance
5. authority denial
6. stale contract denial
7. provenance tampering detection

Expected result: `COGNITIVE ARTIFACT ACTION CLOSURE: 9/9 PASS`.

## Red Team
- Specific-engine laundering: engine is not a Genesis primitive.
- Hidden authority: denied contract is rejected.
- Stale input reuse: input-root mutation changes output/provenance.
- Fake verification: verification recomputes expected content and provenance.
- Replay ambiguity: same envelope must reproduce exactly in the surrogate.
- Overclaim: deterministic surrogate does not prove real LLM determinism, truth, or quality.

## Primitive reduction
No new Genesis primitive is justified by this bounded model. The result supports treating cognition as a replaceable capability/implementation behind an executable contract, with observation/evidence/provenance remaining externalizable semantics.

## Limits
This does not establish semantic equivalence of different LLMs, factual correctness, retrieval quality, human judgment, stochastic reproducibility, or universal cognitive closure. A real Genesis private vector is still required for the private-to-public correspondence gate.
