# Active Independent-Replication Manifest

**Status:** ACTIVE / IR-V2
**Date:** 2026-09-04

This manifest is the single navigation point for the active public clean-room replication surface.

## Active artifacts

| Artifact | Role | Status |
|---|---|---|
| `challenge-v2.json` | frozen neutral challenge bytes | ACTIVE / FROZEN |
| `INDEPENDENT_REPLICATION_CALL.md` | public invitation and submission requirements | ACTIVE |
| `README.md` | active replication surface documentation | ACTIVE |
| `EXTERNAL_PARTICIPANT_RUNBOOK_V1.md` | participant operational procedure | ACTIVE unless superseded by a later runbook explicitly linked here |
| `EXTERNAL_EXECUTION_PACKET_V1.md` | execution/evidence packet contract | ACTIVE unless superseded by a later packet explicitly linked here |
| `EXTERNAL_EXECUTION_AUDIT_PACKET_V1.md` | audit contract | ACTIVE unless superseded explicitly |
| `EXECUTION_ATTESTATION_V1.md` | execution attestation contract | ACTIVE unless superseded explicitly |

## Not active

- `IR-V3_MINIMALITY_CHALLENGE_PROPOSAL.md` — `SUPERSEDED / DESIGN NOTE / NOT ACTIVE / NOT EVIDENCE`.
- IR-V1 challenge/protocol artifacts — historical only.
- Files outside `independent-replication/` are not part of the active IR-V2 challenge unless this manifest explicitly says so.

## Challenge identity

The active challenge identifier is:

`IR-V2`

The SHA-256 required by the replication protocol is the digest of the **exact bytes of `challenge-v2.json`** used by the participant.

Current published content SHA-256:

`03b25456a1ad0b40272daa1ca633910855433cfdce6ece8d0cf9e3352cd7ef1b`

Repository tooling may expose a different 40-hex Git blob SHA-1 for the same file. That identifier is not the content SHA-256 and must never be substituted for it.

## Evidence rule

A file existing in this directory does not make it active evidence. A research result requires the exact challenge revision, raw submission, provenance, commitment/reveal data where applicable, verifier output and subsequent adjudication under the private research protocol.

## Change rule

IR-V2 is frozen for the current replication campaign. Any semantic challenge modification requires a new challenge version and a new manifest entry. Do not modify `challenge-v2.json` in place after a participant has committed to it.

## Security boundary

This public surface must not contain private research, private Genesis artifacts, credentials, unpublished target hypotheses or confidential authority material.
