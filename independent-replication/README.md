# Independent Reconstruction Challenge

This public directory provides a clean-room mechanism for materially independent reconstruction of a minimal semantic basis.

## Active challenge

Use **IR-V2**: `challenge-v2.json`.

Frozen challenge SHA-256:
`03b25456a1ad0b40272daa1ca633910855433cfdce6ece8d0cf9e3352cd7ef1b`

The value above is the SHA-256 of the exact file bytes. The previous 40-hex value was a Git blob SHA-1 and was incorrectly labelled as SHA-256; that documentation error is corrected here. The two hashes must never be conflated.

IR-V1 remains in the repository as historical research infrastructure. IR-V2 is the active challenge because its contract removes the explicit target-category list that was present in V1.

## Independence boundary

This package is intentionally independent of the private research repository. It contains no private source, private corpus, current candidate basis, Genesis reduction map, or canonical decision.

The challenge is not a test of agreement with a pre-existing answer. A materially different basis is a valid research outcome.

## Frozen challenge contract

Every submission MUST include `challenge_sha256`, the SHA-256 of the exact frozen challenge file used for the reconstruction. The verifier recomputes that digest from the supplied challenge path and fails closed on mismatch.

A replication run MUST record both the exact challenge commit/revision and the SHA-256 of the challenge bytes. A Git blob SHA-1, commit SHA, or any other repository identifier is not a substitute for the declared content SHA-256.

This binds the submission to a concrete challenge revision rather than silently accepting the current file as equivalent. Published challenge V2 is immutable for a replication run; semantic changes require a new challenge version rather than rewriting V2 after results are observed.

## Challenge-incompleteness is valid evidence

The listed cases are a bounded public challenge, not a claim that they exhaust the semantic space. An independent participant is explicitly invited to report:

- a missing obligation or domain not represented by the challenge;
- a counterexample that cannot be expressed adequately by the supplied cases;
- a distinction that changes the minimal basis;
- an argument that the challenge itself is biased, circular, over-constrained, or under-specified.

Such findings are first-class research evidence. They must not be rejected merely because the structural verifier does not score them. Participants may preserve them in additional submission fields and in the raw report; the verifier intentionally ignores unknown optional fields rather than treating the published challenge vocabulary as a closed ontology.

## Structured counterexamples

Counterexamples are checked as structured records, not as keywords. Each record must contain:

- `domain` — the relevant domain or context;
- `scenario` — an actual counterexample scenario;
- `failure_if_ignored` — the concrete semantic loss if the distinction is ignored.

This prevents a submission from passing merely by listing required words without supplying an adversarial case. The verifier still does not judge whether the scenario is semantically correct; that remains independent research/adjudication.

## Procedure

1. Freeze the exact challenge revision you received and record its commit/revision plus the SHA-256 above.
2. Work from the challenge only; do not inspect private research or a current candidate basis before commitment.
3. Produce a raw submission containing your basis, case mappings, deletion analysis, structured counterexamples, uncertainty, provenance, candidate visibility, and `challenge_sha256`. Preserve any out-of-challenge obligations or challenge criticisms in the raw result as additional fields or an accompanying report.
4. Compute the commitment over the exact raw result bytes using the declared commit-reveal protocol and publish the commitment with an observable timestamp.
5. After the agreed comparison window, reveal the raw submission and nonce.
6. Run the structural verifier against the exact frozen challenge.
7. Verify the commitment against the exact raw bytes and nonce; publish verifier output, challenge revision, challenge SHA-256, submission commitment, environment, candidate-visibility status, and deviations.
8. Only after reveal compare the reconstruction with any target hypothesis. Adjudication must consider out-of-challenge findings before evaluating agreement.

## What the verifier does not do

It does not contain or test a target ontology. Passing it does not prove semantic adequacy. Disagreement with a private hypothesis is not a failure. It also does not prove that the challenge is complete.

## Blindness warning

Git history of this public repository may reveal prior generic experiments. For strong R3/R4 blindness, use the frozen IR-V2 challenge snapshot without exposure to the target hypothesis and preserve the delivery/provenance path used by the independent participant.

## Security boundary

Do not submit secrets, private Genesis source, private research text, credentials, private datasets, or unpublished authority material.
