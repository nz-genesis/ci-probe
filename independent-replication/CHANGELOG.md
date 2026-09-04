# Replication Kit Changelog

## Current state — 2026-09-04

- **IR-V2 is the active public clean-room challenge.**
- IR-V1 is historical and must not be treated as the active reconstruction challenge.
- The active challenge is bound to the SHA-256 of the exact frozen `challenge-v2.json` bytes.
- Git blob SHA-1 and commit SHA are explicitly not substitutes for the challenge content digest.
- Open-world omissions, missing obligations/domains, counterexamples and challenge-criticism are first-class research outputs.
- The verifier remains structural/reproducibility infrastructure; it does not contain a target ontology or semantic oracle.
- Material independence is evaluated from information flow and provenance, not from prompt changes, directory names or process boundaries alone.
- Raw reconstruction must be frozen before target comparison; commitment/reveal remains part of the high-strength protocol.

## Historical notes

### 2026-09-02 — V1 hardening

- Added immutable frozen-challenge identity and challenge digest binding.
- Added manifest/envelope contract.
- Replaced keyword-only anti-laundering counterexample checks with structured records.
- Made challenge incompleteness and out-of-challenge counterexamples first-class evidence.
- Added public verification and reproducibility contract.
- Preserved V1 challenge bytes unchanged; semantic challenge changes require a new challenge version.

### IR-V2 transition

IR-V2 superseded V1 as the active challenge because the earlier version exposed an explicit target-category list. IR-V2 removes that explicit category list and keeps the public verifier ontology-agnostic.

## Epistemic status

These changes harden the public evidence mechanism. They do **not** constitute an independent reconstruction, prove semantic adequacy, establish minimality, uniqueness or universality, or authorize any private project's canonical decisions.
