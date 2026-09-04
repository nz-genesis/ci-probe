# Independent Replication Protocol

**Status:** ACTIVE PUBLIC PROTOCOL / IR-V2 COMPATIBLE

## Purpose

This repository provides a public, clean-room channel for independent verification and reconstruction experiments. The protocol is designed so that a participant can reconstruct a result without access to private research or an expected answer.

The active reconstruction challenge is maintained under `independent-replication/` and is currently **IR-V2**. The older `independence/` directory is a historical/control surface and is not a second independent evidence lineage.

## Participant flow

1. Select the active frozen challenge revision and record its revision plus content SHA-256.
2. Work only from the supplied public challenge and stated constraints before the raw reconstruction is frozen.
3. Do not inspect or request private repositories, private mappings, unpublished expected results, or private adjudication material.
4. Independently derive the factorization/basis, assumptions, counterexamples, negative results and unresolved cases required by the challenge.
5. Freeze the raw substantive result before any comparison with a target hypothesis.
6. Create a random nonce and compute the commitment over the exact raw submission bytes.
7. Publish the commitment together with the exact challenge content hash. This is the public freeze point.
8. Keep the raw submission and nonce unchanged until reveal.
9. After the agreed reveal point, publish the exact raw bytes and nonce.
10. Run the structural verifier against the exact frozen challenge and verify the commitment.
11. Only after reveal may a private adjudicator perform substantive comparison.

## Challenge binding

Every submission MUST include:

- `challenge_id`;
- `challenge_version`;
- `challenge_sha256`, computed from the exact frozen challenge bytes;
- the exact challenge commit/revision used;
- candidate-visibility status;
- independence/provenance statement.

A Git blob SHA-1 or commit SHA is not a substitute for `challenge_sha256`.

## Commit-reveal rule

The commitment is:

`SHA256(raw_submission_bytes + UTF-8 newline byte + nonce_UTF8)`

The verifier checks integrity and challenge binding only. It is intentionally not a semantic oracle and contains no target ontology or expected answer.

A commitment without a later exact reveal is provenance metadata, not substantive research evidence.

## Required submission content

At minimum:

- independently derived basis/factorization;
- case-by-case mapping to the frozen challenge;
- removal/reduction analysis;
- strongest counterexample found;
- negative or unresolved results;
- methodology and assumptions;
- provenance and environment;
- candidate-visibility statement;
- exact challenge revision and SHA-256;
- raw artifact reference or exact bytes;
- timestamp.

Additional out-of-challenge findings MUST be preserved rather than discarded merely because the structural verifier ignores unknown optional fields.

## Independence boundary

A different prompt, model, process, account or directory does not automatically constitute material independence. Independence is evaluated from information flow and provenance.

For a high-strength result, the participant must not inspect private target material or prior private hypotheses before raw freeze. The participant's own provenance must establish what model/provider/runtime/operator or team performed the reconstruction, to the extent necessary for the applicable review.

## Contamination

If expected semantics, private target material, or other disallowed information were exposed before raw freeze, mark the run contaminated and do not present it as materially independent evidence.

If contamination occurs after raw freeze but before reveal, preserve the event in provenance and do not alter the committed raw bytes.

## Evidence boundary

The public verifier may establish only what it actually checks:

- schema validity;
- challenge binding;
- cryptographic integrity;
- deterministic structural consistency;
- executable consistency where applicable.

It does not establish semantic adequacy, global minimality, universality, uniqueness, or agreement with any private hypothesis.

## Relation to repository surfaces

```text
independent-replication/
    ACTIVE IR-V2 clean-room surface

independence/
    HISTORICAL / CONTROL surface
    NOT a second independent evidence lineage
```

Public generic probes elsewhere in the repository remain substrate experiments. They are not automatically part of the independent reconstruction challenge.

## Security

Do not submit secrets, private source, private research, credentials, private datasets or confidential authority material.

## Interpretation

Disagreement is a valid result. A materially different factorization, missing obligation, challenge criticism or conclusion that no finite universal basis is defensible is valuable evidence and must be preserved for adjudication.
