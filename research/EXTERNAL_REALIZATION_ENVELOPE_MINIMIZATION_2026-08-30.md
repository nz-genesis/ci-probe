# External Realization Envelope Minimization — 2026-08-30

## Scope

Generic clean-room experiment only. No private Genesis hypotheses, credentials, internal endpoints, private datasets, or canonical decisions are included.

## Question

What is the smallest public envelope that prevents semantically relevant private mutations from becoming indistinguishable at an external realization boundary?

## Baseline negative control

The preceding projection experiment showed that a simple allow-listed projection can hide mutations to authority, resource version, temporal constraint, and verification. That result is not repeated here; this experiment changes the variable by adding a minimal decision/provenance envelope.

## Candidate envelope

The candidate carries:

- generic operation inputs;
- a private-side admission consequence (`allow` / `deny`), without exporting the underlying authority/resource/temporal facts;
- a provenance commitment over the private semantic fields;
- the public realization request.

Verification remains private and is not exported as a predicate.

## Local deterministic result

The experiment passes its bounded checks:

- authority mutation changes the provenance commitment and changes the observable realization outcome;
- resource-version mutation changes the provenance commitment and changes the observable realization outcome;
- temporal-state mutation changes the provenance commitment and changes the observable realization outcome;
- verification mutation changes the provenance commitment while leaving admission unchanged, preserving the distinction for private post-execution verification rather than incorrectly exposing verification semantics to the public executor.

## Interpretation

This is evidence that a boundary can preserve some semantically relevant consequences without exporting the private facts that caused them. It is **not** proof of a universally sufficient envelope.

The experiment still does not test dynamic delegation races, concurrent revocation, replay resistance against a real external channel, cryptographic authenticity, physical-world effects, or adversarial public executor behavior.

## CI evidence

The workflow is configured to execute the exact artifact on GitHub-hosted Actions. The public CI run for this exact experiment must be recorded separately from the local deterministic result; a workflow file or local PASS is not execution evidence.

## Next bounded tests

1. mutation of admission decision/provenance independently to test authority laundering and provenance substitution;
2. replay/stale envelope test;
3. post-effect evidence tampering test;
4. public executor equivocation test;
5. private verification of returned evidence against the original private contract.

## Status

`LOCAL PASS / PUBLIC CI PENDING / EXPERIMENTAL`
