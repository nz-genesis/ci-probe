# Independent Reconstruction Challenge

This public directory provides a clean-room mechanism for independent reconstruction of a minimal semantic basis.

## Independence boundary

This package is intentionally independent of the private research repository. It contains no private source, private corpus, current candidate basis, Genesis reduction map, or canonical decision.

The challenge is not a test of agreement with a pre-existing answer. A materially different basis is a valid research outcome.

## Frozen challenge contract

Every submission MUST include `challenge_sha256`, the SHA-256 of the exact frozen challenge file used for the reconstruction. The verifier recomputes that digest from the supplied challenge path and fails closed on mismatch.

This binds the submission to a concrete challenge revision rather than silently accepting the current file as equivalent. Published challenge V1 is immutable for a replication run; semantic changes require a new challenge version rather than rewriting V1 after results are observed.

## Challenge-incompleteness is valid evidence

The listed cases are a bounded public challenge, not a claim that they exhaust the semantic space. An independent participant is explicitly invited to report:

- a missing obligation or domain not represented by the challenge;
- a counterexample that cannot be expressed adequately by the supplied cases;
- a distinction that changes the minimal basis;
- an argument that the challenge itself is biased, circular, over-constrained, or under-specified.

Such findings are first-class research evidence. They must not be rejected merely because the structural verifier does not score them. Participants may preserve them in additional submission fields and in the raw report; the verifier intentionally ignores unknown optional fields rather than treating the published challenge vocabulary as a closed ontology.

## Structured counterexamples

The six anti-laundering topics (`authority`, `evidence`, `identity`, `provenance`, `execution`, `relation`) are checked as structured records, not as keywords. Each record must contain:

- `topic` — the attacked semantic distinction;
- `scenario` — an actual counterexample scenario;
- `failure_if_ignored` — the concrete semantic loss if the distinction is ignored.

This prevents a submission from passing merely by listing the required words without supplying an adversarial case. The verifier still does not judge whether the scenario is semantically correct; that remains independent research/adjudication.

## Procedure

1. Freeze the challenge revision you received.
2. Work from the challenge only; do not inspect private research or a current candidate basis before commitment.
3. Produce a raw submission containing your basis, case mappings, deletion analysis, structured counterexamples, uncertainty, provenance, candidate visibility, and `challenge_sha256`. Preserve any out-of-challenge obligations or challenge criticisms in the raw result as additional fields or an accompanying report.
4. Compute SHA-256 of the exact raw result and publish the commitment with an observable timestamp.
5. After the agreed comparison window, reveal the raw submission.
6. Run `python independent-replication/verify_submission.py submission.json` against the exact frozen challenge.
7. Publish verifier output, challenge commit, challenge SHA-256, submission hash, environment, candidate-visibility status, and deviations.
8. Only after reveal compare the reconstruction with any target hypothesis. Adjudication must consider out-of-challenge findings before evaluating agreement.

## What the verifier does not do

It does not contain or test a target ontology. Passing it does not prove semantic adequacy. Disagreement with a private hypothesis is not a failure. It also does not prove that the challenge is complete.

## Blindness warning

Git history of this public repository may reveal prior generic experiments. For strong R3/R4 blindness, use a separately published challenge snapshot whose provenance predates the reconstruction and whose delivery path does not expose the target hypothesis.

## Security boundary

Do not submit secrets, private Genesis source, private research text, credentials, private datasets, or unpublished authority material.
