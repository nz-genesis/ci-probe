# Independent Reconstruction Challenge

This public directory provides a clean-room mechanism for independent reconstruction of a minimal semantic basis.

## Independence boundary

This package is intentionally independent of the private research repository. It contains no private source, private corpus, current candidate basis, Genesis reduction map, or canonical decision.

The challenge is not a test of agreement with a pre-existing answer. A materially different basis is a valid research outcome.

## Frozen challenge contract

Every submission MUST include `challenge_sha256`, the SHA-256 of the exact frozen challenge file used for the reconstruction. The verifier recomputes that digest from the supplied challenge path and fails closed on mismatch.

This binds the submission to a concrete challenge revision rather than silently accepting the current file as equivalent.

## Procedure

1. Freeze the challenge revision you received.
2. Work from the challenge only; do not inspect private research or a current candidate basis before commitment.
3. Produce a raw submission containing your basis, case mappings, deletion analysis, counterexamples, uncertainty, provenance, candidate visibility, and `challenge_sha256`.
4. Compute SHA-256 of the exact raw result and publish the commitment with an observable timestamp.
5. After the agreed comparison window, reveal the raw submission.
6. Run `python independent-replication/verify_submission.py submission.json` against the exact frozen challenge.
7. Publish verifier output, challenge commit, challenge SHA-256, submission hash, environment, candidate-visibility status, and deviations.
8. Only after reveal compare the reconstruction with any target hypothesis.

## What the verifier does not do

It does not contain or test a target ontology. Passing it does not prove semantic adequacy. Disagreement with a private hypothesis is not a failure.

## Blindness warning

Git history of this public repository may reveal prior generic experiments. For strong R3/R4 blindness, use a separately published challenge snapshot whose provenance predates the reconstruction and whose delivery path does not expose the target hypothesis.

## Security boundary

Do not submit secrets, private Genesis source, private research text, credentials, private datasets, or unpublished authority material.
