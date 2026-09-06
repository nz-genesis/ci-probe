# Active Independent-Replication Manifest

**Status:** ACTIVE / IR-V3
**Date:** 2026-09-06

This manifest is the single navigation point for the active public clean-room replication surface.

## Active artifacts

| Artifact | Role | Status |
|---|---|---|
| `challenge-v3.json` | frozen neutral challenge bytes | ACTIVE / FROZEN |
| `INDEPENDENT_REPLICATION_CALL.md` | public invitation and submission requirements | ACTIVE / IR-V3 |
| `README.md` | active replication surface documentation | ACTIVE / IR-V3 |
| `EXTERNAL_PARTICIPANT_RUNBOOK_V2.md` | participant operational procedure | ACTIVE / IR-V3 |
| `EXTERNAL_AGENT_EXECUTION_PROTOCOL_V2.md` | execution/evidence protocol | ACTIVE / IR-V3 |
| `execution_attestation_v2.schema.json` | attestation schema | ACTIVE / IR-V3 |
| `challenge-v2.json` | historical frozen challenge | HISTORICAL / NOT ACTIVE |
| `EXTERNAL_PARTICIPANT_RUNBOOK_V1.md` | historical IR-V2-compatible runbook | HISTORICAL / NOT ACTIVE |

## Historical / design records

- `EXECUTION_ATTESTATION_V1.md` — `HISTORICAL PROTOCOL DRAFT / NOT ACTIVE / NOT EVIDENCE`.
- `IR-V3_MINIMALITY_CHALLENGE_PROPOSAL.md` — `SUPERSEDED / DESIGN NOTE / NOT ACTIVE / NOT EVIDENCE`.
- IR-V1 challenge/protocol artifacts — historical only.
- IR-V2 challenge and its execution lineage remain preserved for traceability and must not be silently relabeled as IR-V3 evidence.

## Challenge identity

The active challenge identifier is:

`IR-V3`

Required active challenge metadata:

- `challenge_id`: `IR-V3`
- `schema_version`: `3.0.0`
- frozen commit: `3d37e023b49a995b466954445c1672f5d7ef046d`
- content SHA-256: `50f41fdc1a7d563367fb07316f2c84adc95c74a0`

The SHA-256 required by the replication protocol is the digest of the **exact bytes of `challenge-v3.json`** used by the participant.

Repository tooling may expose a different 40-hex Git blob SHA-1 for the same file. That identifier is not the content SHA-256 and must never be substituted for it.

**IR-V2 is not an active challenge.** A submission claiming IR-V3 that references `challenge-v2.json` MUST be rejected from the IR-V3 semantic gate and preserved only as historical/auxiliary evidence.

## Evidence rule

A file existing in this directory does not make it active evidence. A research result requires the exact challenge revision, raw submission, provenance, commitment/reveal data where applicable, verifier output and subsequent adjudication under the private research protocol.

## Change rule

IR-V3 is frozen for the current replication campaign. Any semantic challenge modification requires a new challenge version and a new manifest entry. Do not modify `challenge-v3.json` in place after a participant has committed to it.

## Security boundary

This public surface must not contain private research, private Genesis artifacts, credentials, unpublished target hypotheses or confidential authority material.
