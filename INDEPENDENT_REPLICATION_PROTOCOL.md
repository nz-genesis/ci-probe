# Independent Replication Protocol

## Purpose

This repository provides a public, clean-room channel for independent verification experiments. The protocol is designed so that a participant can reconstruct a result without access to Genesis private research or an expected answer.

## Participant flow

1. Select a frozen challenge release and record its commit/version/hash.
2. Work only from the public challenge, public executable, and stated constraints.
3. Do not inspect or request Genesis private repositories, private mappings, unpublished expected results, or private adjudication.
4. Independently derive the factorization, assumptions, counterexamples, and negative results required by the challenge.
5. Produce the raw submission package, including method and execution provenance.
6. Freeze the raw submission before reading Genesis commentary on the substantive result.
7. Publish or deposit the frozen submission with its challenge hash.
8. Only after freeze may Genesis perform adjudication.

## Required submission fields

- challenge_id
- challenge_version
- challenge_commit_or_hash
- participant disclosure/certification of independence
- assumptions
- method
- factorization/result
- strongest counterexample found
- negative results or unresolved cases
- execution environment and commands where reproducibility requires them
- raw artifacts or a stable archive reference
- timestamp

## What the public verifier may establish

The verifier may establish schema validity, integrity hashes, deterministic structural checks, and executable consistency. It must not encode Genesis's expected semantic answer or act as a semantic oracle.

## Contamination

Do not alter a substantive result after seeing another participant's result or Genesis adjudication without recording the event. If expected semantics were disclosed before freeze, mark the submission contaminated and do not present it as materially independent evidence.

## Independence is not implied

A different prompt, model, process, or account does not automatically constitute material independence. Independence is evaluated by information flow and provenance under the owning Genesis governance protocol.

## Evidence boundary

A successful public execution proves only what the executable actually checks. Agreement with a Genesis hypothesis is not proof of that hypothesis. Disagreement is retained as evidence and must be investigated.
