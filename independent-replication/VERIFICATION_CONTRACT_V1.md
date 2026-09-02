# Verification Contract V1

## Scope

This document defines the public structural verification boundary. It is deliberately weaker than semantic adjudication.

## Required integrity

1. Submission declares `challenge_sha256`.
2. Verifier recomputes SHA-256 of the exact supplied challenge bytes.
3. Mismatch is a hard failure.
4. A replication run records the challenge origin commit and digest.
5. Frozen V1 challenge content is never edited in place; changes create a new challenge version.

## Required reconstruction evidence

A submission must map every published challenge case to its proposed basis and provide deletion/reconstruction analysis for every basis element.

Counterexamples are structured records with:

- `topic`
- `scenario`
- `failure_if_ignored`

The required topics are `authority`, `evidence`, `identity`, `provenance`, `execution`, and `relation`. Keyword-only lists do not satisfy the contract.

## Open-world clause

The challenge is not assumed complete. Participants may add out-of-challenge obligations, domains, distinctions, counterexamples, and challenge-bias findings using additional fields or an accompanying report. The structural verifier ignores unknown optional fields; private adjudication must consider them.

## Non-claims

A verifier PASS does not establish:

- semantic adequacy;
- truth of a participant's basis;
- challenge completeness;
- intellectual independence;
- correspondence with Genesis;
- minimality;
- Universal Minimality;
- Canon.

## Reproducibility record

A published run should include:

`challenge origin commit + challenge SHA-256 + verifier commit/SHA-256 + submission SHA-256 + environment + provider/team + candidate visibility + timestamp + deviations + verifier output`.

## Blindness

Git history can leak generic prior experiments. Strong R3/R4 work therefore uses a separately frozen delivery snapshot whose creation and delivery do not expose the target hypothesis.
