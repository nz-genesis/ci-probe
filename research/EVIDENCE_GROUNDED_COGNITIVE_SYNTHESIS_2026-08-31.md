# Evidence-Grounded Cognitive Synthesis — 2026-08-31

**Status:** EXPERIMENTAL / EXECUTABLE / HOSTED-CI PENDING

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

## Local result
The exact clean-room logic is designed to emit `EVIDENCE-GROUNDED COGNITIVE SYNTHESIS: 8/8 PASS` when executed. The repository artifact was committed, but hosted CI must be inspected before claiming execution of the committed copy.

## Red Team
1. Unsupported claim laundering — rejected by independent fact membership check.
2. Unauthorized source injection — rejected before synthesis.
3. Contradiction smoothing — rejected; contradiction remains explicit failure.
4. Provenance forgery — rejected by recomputed evidence root.
5. Evidence removal — changes root and removes the dependent beta claim.
6. Self-corroboration — synthesis output is not accepted as its own evidence.
7. Engine laundering — no LLM/retriever/engine field is required by the semantic contract.

## Primitive reduction
No new primitive is justified. The tested responsibility can be represented through existing candidate concepts: Capability, Contract, Authority, Constraint/Version, Evidence, Observation, Verification, Lineage/Provenance, State.

## Boundary
This does not prove factual correctness of arbitrary real-world cognition, retrieval quality, semantic completeness, or LLM reliability. It proves only the bounded evidence-governance property represented by the fixture.

## Next discriminator
The next stronger test should use materially heterogeneous evidence with temporal validity and source disagreement, then test whether claim admission can remain evidence-bounded under stale and adversarial sources. A separate irreversible-world-effect line remains open.
