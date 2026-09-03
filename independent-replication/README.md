# Independent Reconstruction Challenge

This public directory provides a clean-room mechanism for materially independent reconstruction of a minimal semantic basis.

## Active challenge

Use **IR-V2**: `challenge-v2.json`.

The exact challenge bytes are the sole authority for `challenge_sha256`. The verifier computes SHA-256 directly from the supplied frozen challenge file and rejects a submission whose declared digest does not match. **Do not copy a digest from Git history, a Git blob SHA, or stale documentation.**

A previous version of this README incorrectly published a value as the SHA-256 of IR-V2. That value was not independently verified against the current challenge bytes and is removed here. The Git blob identifier shown by repository tooling is SHA-1 and must never be labelled SHA-256.

IR-V1 remains in the repository as historical research infrastructure. IR-V2 is the active challenge because its contract removes the explicit target-category list that was present in V1.

## Independence boundary

This package is intentionally independent of the private research repository. It contains no private source, private corpus, current candidate basis, Genesis reduction map, or canonical decision.

The challenge is not a test of agreement with a pre-existing answer. A materially different basis is a valid research outcome.

## Frozen challenge contract

Every submission MUST include `challenge_sha256`, the SHA-256 of the exact frozen challenge file used for the reconstruction. The verifier recomputes that digest from the supplied challenge path and fails closed on mismatch.

A replication run MUST record both the exact challenge commit/revision and the SHA-256 computed from the challenge bytes. A Git blob SHA-1, commit SHA, or any other repository identifier is not a substitute for the declared content SHA-256.

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

## Blind execution boundary

`run_blind_solver.py` provides the execution boundary for a blind participant process. It passes the frozen challenge to a separately invoked solver process, captures the raw result, records challenge/result digests and redacted provenance, and refuses to publish a frozen bundle when the solver fails. Its regression suite covers failure secrecy and non-publication of solver invocation details.

This process boundary is necessary but is **not sufficient for material external independence**. A solver running in a separate process can still share the same model lineage, operator, credentials, hidden context, or research incentives. Therefore a run through this harness is classified as `RAW_BLIND_RUN; NOT_EXTERNAL_INDEPENDENCE_BY_ITSELF` until the participant/runtime provenance establishes the stronger independence claim required by the applicable protocol.

For a high-strength blind run, the participant must receive only the frozen challenge and minimal contract, must not receive private Genesis material or prior target hypotheses, and must freeze the raw output before any target comparison. The review actor must not receive Genesis interpretation before attacking the frozen result.

## Procedure

1. Freeze the exact challenge revision you received and record its commit/revision.
2. Compute and record SHA-256 from those exact challenge bytes; do not substitute a Git blob SHA-1.
3. Work from the challenge only; do not inspect private research or a current candidate basis before commitment.
4. Produce a raw submission containing your basis, case mappings, deletion analysis, structured counterexamples, uncertainty, provenance, candidate visibility, and `challenge_sha256`. Preserve any out-of-challenge obligations or challenge criticisms in the raw result as additional fields or an accompanying report.
5. Compute the commitment over the exact raw result bytes using the declared commit-reveal protocol and publish the commitment with an observable timestamp.
6. After the agreed comparison window, reveal the raw submission and nonce.
7. Run the structural verifier against the exact frozen challenge.
8. Verify the commitment against the exact raw bytes and nonce; publish verifier output, challenge revision, challenge SHA-256, submission commitment, environment, candidate-visibility status, and deviations.
9. Only after reveal compare the reconstruction with any target hypothesis. Adjudication must consider out-of-challenge findings before evaluating agreement.

## What the verifier does not do

It does not contain or test a target ontology. Passing it does not prove semantic adequacy. Disagreement with a private hypothesis is not a failure. It also does not prove that the challenge is complete.

## Blindness warning

Git history of this public repository may reveal prior generic experiments. For strong R3/R4 blindness, use the frozen IR-V2 challenge snapshot without exposure to the target hypothesis and preserve the delivery/provenance path used by the independent participant.

## Security boundary

Do not submit secrets, private Genesis source, private research text, credentials, private datasets, or unpublished authority material.
