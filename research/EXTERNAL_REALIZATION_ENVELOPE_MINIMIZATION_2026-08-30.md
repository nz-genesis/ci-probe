# External Realization Envelope Minimization — 2026-08-30

## Scope

Generic clean-room experiment only. No private Genesis hypotheses, credentials, internal endpoints, private datasets, or canonical decisions are included.

## Question

What is the smallest public envelope that prevents semantically relevant private mutations from becoming indistinguishable at an external realization boundary?

## Prior negative control

The preceding simple-projection experiment established collisions for private authority, resource-version, temporal-state, and verification mutations when only generic operation inputs crossed the boundary. That result is not repeated here; this experiment changes the variable by adding a minimal boundary consequence and provenance commitment.

## Candidate envelope

The candidate carries:

- generic operation inputs;
- a private-side admission consequence (`allow` / `deny`) without exporting the underlying authority/resource/temporal facts;
- a provenance commitment over the private semantic fields;
- the public realization request.

Verification remains private and is not exported as a public predicate.

## Local deterministic result

The exact artifact `external_realization_envelope_minimization.py` passes its bounded checks:

- authority mutation: provenance changes and realization changes from applied to not-applied;
- resource-version mutation: provenance changes and realization changes from applied to not-applied;
- temporal-state mutation: provenance changes and realization changes from applied to not-applied;
- verification mutation: provenance changes while admission remains unchanged, leaving verification to private post-execution interpretation.

This demonstrates a bounded preservation pattern, not universal sufficiency.

## Public execution evidence

The exact workflow `.github/workflows/external-realization-envelope-minimization.yml` was added at commit `646a9961b5cb34245bea37d7e19ff00513789732`. The workflow is configured for GitHub-hosted Actions and the public repository is currently executing many push-triggered workflows successfully. A contemporaneous public run `33304157974`, job `99237608085`, reached `Set up job`, `Checkout`, execution, `Post Checkout`, and `Complete job` successfully.

The connector could not resolve the exact new workflow's own run from the available public Actions listing, so that unrelated success is deliberately **not** substituted for exact CI evidence. Status remains `PUBLIC CI PENDING` for the exact envelope artifact.

## Competing hypotheses

### H1 — Simple projection is sufficient

Rejected by the prior mutation collision experiment.

### H2 — Boundary consequence + provenance commitment is sufficient for the tested bounded class

Supported by local deterministic evidence, pending exact live-channel execution and adversarial boundary tests.

### H3 — Any external realization necessarily requires disclosure of the full private semantic contract

Not supported by the bounded local result because selected semantic consequences can be preserved without publishing the underlying private values.

### H4 — The candidate envelope is a Genesis primitive

No evidence. Not promoted.

## Red-Team obligations still open

1. authority laundering: substitute or forge the admission consequence;
2. provenance substitution: reuse a commitment from another semantic contract;
3. replay/stale envelope;
4. post-effect evidence tampering;
5. public executor equivocation;
6. UNKNOWN / partial effect across the boundary;
7. repeated-observation reconstruction of private semantics;
8. verification-rule mutation after effect;
9. identity/request mix-up;
10. boundary failure where public execution succeeds but private verification rejects the evidence.

## Omission gate

This pass does not establish:

- dynamic delegation/revocation races;
- concurrent mutation of authority while external realization is executing;
- cryptographic authenticity of the envelope;
- arbitrary distributed clocks or causal ordering;
- multi-step irreversible effects;
- physical-world verification;
- universal privacy against adaptive query access;
- global minimality.

These remain explicit unresolved boundaries.

## Status

`LOCAL PASS / PUBLIC CI PENDING / EXPERIMENTAL`

## Next bounded pass

Obtain exact CI evidence if the workflow run becomes observable, then run provenance-substitution, replay/staleness, equivocation, evidence-tampering, and private-verification tests. The decisive criterion is whether a private semantic mutation that should change the correct realization/evidence outcome can remain indistinguishable across the boundary without unacceptable disclosure or authority transfer.
