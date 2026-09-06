# Independent Reconstruction Challenge

This public directory provides a clean-room mechanism for materially independent reconstruction of a minimal semantic basis.

## Active challenge

Use **IR-V3**: `challenge-v3.json`.

Required active challenge identity:

- `challenge_id`: `IR-V3`
- `schema_version`: `3.0.0`
- frozen commit: `3d37e023b49a995b466954445c1672f5d7ef046d`
- content SHA-256: `50f41fdc1a7d563367fb07316f2c84adc95c74a0`

The exact challenge bytes are the sole authority for `challenge_sha256`. The participant MUST compute SHA-256 directly from the exact supplied frozen challenge file. **Do not copy a digest from Git history, a Git blob SHA, or stale documentation.**

**Do not use `challenge-v2.json` for an IR-V3 submission.** IR-V2 remains preserved as historical research infrastructure and auxiliary evidence only.

## Independence boundary

This package is intentionally independent of the private research repository. It contains no private source, private corpus, current candidate basis, Genesis reduction map, or canonical decision.

The challenge is not a test of agreement with a pre-existing answer. A materially different basis is a valid research outcome.

## Frozen challenge contract

Every submission MUST include `challenge_sha256`, the SHA-256 of the exact frozen challenge file used for the reconstruction. The verifier recomputes that digest from the supplied challenge path and fails closed on mismatch.

A replication run MUST record the exact challenge commit/revision and the SHA-256 computed from the challenge bytes. A Git blob SHA-1, commit SHA, or any other repository identifier is not a substitute for the declared content SHA-256.

IR-V3 is frozen for the current replication campaign. Semantic changes require a new challenge version rather than rewriting V3 after results are observed.

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

For a high-strength blind run, the participant must receive only the frozen IR-V3 challenge and minimal public execution contract, must not receive private Genesis material or prior target hypotheses, and must freeze the raw output before any target comparison. The review actor must not receive Genesis interpretation before attacking the frozen result.

## Procedure

1. Freeze the exact IR-V3 challenge revision you received and record its commit/revision.
2. Verify `challenge_id = IR-V3` and `schema_version = 3.0.0`.
3. Compute and record SHA-256 from those exact challenge bytes; do not substitute a Git blob SHA-1.
4. Work from the challenge and public execution protocol only; do not inspect private research or a current candidate basis before commitment.
5. Produce a raw submission containing your basis, case mappings, deletion analysis, explicit composition rules, structured counterexamples, uncertainty, minimality objective, H4 treatment, provenance, candidate visibility, and `challenge_sha256`. Preserve any out-of-challenge obligations or challenge criticisms in the raw result as additional fields or an accompanying report.
6. Freeze the exact raw result before target comparison.
7. Compute the raw-result SHA-256 and create the commitment required by the active protocol before target comparison.
8. Preserve the exact raw bytes and attestation/commitment material needed for later reveal.
9. Run the structural verifier against the exact frozen challenge.
10. Submit the raw result, execution attestation v2, commitment/reveal evidence and provenance declaration.
11. Only after integrity/provenance review compare the reconstruction with any target hypothesis. Adjudication must consider out-of-challenge findings before evaluating agreement.

## What the verifier does not do

It does not contain or test a target ontology. Passing it does not prove semantic adequacy. Disagreement with a private hypothesis is not a failure. It also does not prove that the challenge is complete.

## Blindness warning

Git history of this public repository may reveal prior generic experiments. For strong blindness, use the frozen IR-V3 challenge snapshot without exposure to the target hypothesis and preserve the delivery/provenance path used by the independent participant.

## Security boundary

Do not submit secrets, private Genesis source, private research text, credentials, private datasets, or unpublished authority material.
