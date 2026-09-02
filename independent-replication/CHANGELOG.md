# Replication Kit Changelog

## 2026-09-02 — V1 hardening

- Added immutable frozen-challenge identity and `challenge_sha256` binding.
- Added manifest/envelope contract.
- Replaced keyword-only anti-laundering counterexample checks with structured records containing `topic`, `scenario`, and `failure_if_ignored`.
- Explicitly made challenge incompleteness and out-of-challenge counterexamples first-class evidence.
- Added a public verification contract documenting non-claims and required reproducibility records.
- Added/retained CI tests for syntax, JSON, frozen challenge integrity, and challenge substitution.
- Kept V1 challenge bytes unchanged; semantic challenge changes require a new version.

## Epistemic status

These changes harden the evidence mechanism. They do not constitute an independent reconstruction, prove semantic adequacy, establish minimality, or authorize Canon.
