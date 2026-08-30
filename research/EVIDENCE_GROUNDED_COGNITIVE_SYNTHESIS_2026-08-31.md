# Evidence-Grounded Cognitive Synthesis — 2026-08-31

**Status:** EXPERIMENTAL / EXECUTABLE / LOCAL PASS / HOSTED-CI PENDING

## Question
Can a cognitive/knowledge-producing action remain bounded by an evidence set, preserve claim provenance, expose contradictions rather than silently resolve them, and be independently verified without introducing a cognition- or retrieval-specific Genesis primitive?

## Non-duplication
This pass is not another replay, coordinator, environment-symmetry, or generic artifact-creation test. The discriminator is epistemic: source-bounded claim formation and independent verification.

## Model
Two allowed sources contain facts. Synthesis produces claims carrying an evidence-root hash and source IDs. Verification independently reconstructs the root and checks that every claim is directly supported by an allowed source.

Negative cases:
- unsupported/forged claim;
- unauthorized evidence source;
- contradictory sources;
- provenance tampering;
- removal of a causally necessary source.

## Red Team correction
The first committed fixture version contained an invalid removal witness: source A already contained the `beta` fact, so removing source B did not actually remove beta. Independent execution caught the false assertion before any PASS was accepted. The fixture was corrected so A supplies only alpha while B uniquely supplies beta. The corrected logic was then independently executed and produced `8/8 PASS`.

This correction is retained as negative research evidence. No result from the defective fixture is counted.

## Local result
The corrected executable logic produced `EVIDENCE-GROUNDED COGNITIVE SYNTHESIS: 8/8 PASS` in an independent execution environment. The committed repository copy is locally verified for the bounded model. Hosted CI has not yet produced a completed run and is not claimed.

## Red Team
1. Unsupported claim laundering — rejected by independent fact membership check.
2. Unauthorized source injection — rejected before synthesis.
3. Contradiction smoothing — rejected; contradiction remains explicit failure.
4. Provenance forgery — rejected by recomputed evidence root.
5. Evidence removal — B is now the unique source of beta; removing B removes beta.
6. Self-corroboration — synthesis output is not accepted as its own evidence.
7. Engine laundering — no LLM/retriever/engine field is required by the semantic contract.
8. Fixture self-validation — independently executed after the initial witness defect was found and corrected.

## Primitive reduction
No new primitive is justified. The tested responsibility can be represented through existing candidate concepts: Capability, Contract, Authority, Constraint/Version, Evidence, Observation, Verification, Lineage/Provenance, State.

## Boundary
This does not prove factual correctness of arbitrary real-world cognition, retrieval quality, semantic completeness, or LLM reliability. It proves only the bounded evidence-governance property represented by the fixture.

## Next discriminator
Use materially heterogeneous evidence with temporal validity and source disagreement, then test whether claim admission remains evidence-bounded under stale and adversarial sources. A separate irreversible-world-effect line remains open.
