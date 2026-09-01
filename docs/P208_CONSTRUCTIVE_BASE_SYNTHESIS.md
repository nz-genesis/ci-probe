# P208 — Constructive Base Synthesis

## Scope

P208 is a bounded clean-room test of whether four representative action classes can be constructed from the current seven-element Genesis candidate basis without introducing a new semantic primitive.

Candidate basis under test:

- State
- Transition
- Capability
- Authority
- Observation
- Evidence
- Constraint

Runtime, execution, persistence, recovery, interaction, presentation, providers, adapters, and principals are treated as realization/context mechanisms or values, not as additional Genesis primitives in this test.

## Action classes

1. Local state transition.
2. Cognitive/artifact production through an external provider capability.
3. External-world effect through an adapter capability.
4. Protected meta-change requiring authority.

## Red Team

The hosted probe attacks:

- capability without authority;
- cognition bypass;
- duplicate external effect;
- stale revocation;
- goal/effect mismatch;
- unauthorized meta-change;
- extension mutation of the core basis;
- LLM dependence as a primitive;
- rich-memory dependence as a primitive;
- UI/headless dependence;
- undeclared primitive inflation;
- observation being treated as execution;
- UNKNOWN being treated as success.

## Evidence protocol

The cumulative `CI Probe` workflow checks out the exact triggering `GITHUB_SHA`, verifies `HEAD == GITHUB_SHA`, executes the probe, and preserves the existing public execution evidence chain.

CI PASS is evidence that the probe executed successfully. It is not, by itself, proof of Genesis semantic correctness or canonical ontology.

## Falsifier

P208 is falsified if any representative action class requires a semantic primitive outside the seven-element candidate basis, or if a Red-Team attack can bypass the stated authority/evidence/constraint boundaries without adding a primitive.
