# IR-V3 Hash Binding Clarification

**Date:** 2026-09-06

This note clarifies hash terminology without modifying the frozen IR-V3 challenge or its historical commit.

## Critical distinction

For `challenge-v3.json`, there are two different identifiers:

1. **Git blob SHA-1** — the 40-hex Git object identifier. The value currently embedded in the frozen challenge's `sha` field is `50f41fdc1a7d563367fb07316f2c84adc95c74a0` and matches the Git blob identifier exposed for that file.
2. **Content SHA-256** — the 64-hex digest computed over the exact bytes of the file. This is the digest required by the IR-V3 execution protocol.

These values MUST NOT be conflated.

The frozen challenge itself is immutable. This note does not alter `challenge-v3.json`, its commit, or its historical evidence lineage.

## Participant verification rule

A participant MUST:

- fetch the exact bytes of `challenge-v3.json` from the specified frozen commit;
- verify `challenge_id = IR-V3` and `schema_version = 3.0.0`;
- compute a fresh SHA-256 digest over those exact bytes;
- compare that 64-hex digest against the protocol-bound content SHA-256 published in the active manifest/runbook.

A Git blob SHA-1, Git commit SHA, display URL, or filename is not a substitute for the content SHA-256.

## Interpretation of the 2026-09-06 participant run

The participant correctly stopped before semantic work when their local interpretation appeared to show a challenge-integrity mismatch. However, their observed `50f41f...` value was the Git blob SHA-1 embedded in the challenge, not the required SHA-256 of exact bytes. Therefore their reported "content SHA mismatch" is not, by itself, evidence that the frozen challenge bytes are corrupted.

The run remains useful as a **verification-apparatus / protocol-clarity test** because it exposed that the public artifact can be misread as binding a Git object SHA where the protocol requires a content SHA-256.

The absence of `execution_attestation_v2.schema.json` at the historical frozen challenge commit is not independently a defect: the v2 schema is a later public apparatus artifact on `main`, while the frozen challenge commit remains immutable.

## Non-retroactivity

This clarification MUST NOT be used to reinterpret the participant's already-frozen run as a semantic replication. No semantic reconstruction occurred, no target comparison occurred, and no Genesis candidate was exposed.

A fresh participant SHOULD use the current active runbook/protocol and the explicitly bound content SHA-256 before semantic work.
