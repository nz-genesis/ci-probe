# Received blind submission — provenance audit

Status: `RAW INTEGRITY VERIFIED / MATERIAL INDEPENDENCE UNDETERMINED`

Date: 2026-09-04

## Scope

This audit evaluates the received raw submission without using its semantic agreement with any target basis as evidence of correctness. It checks only challenge identity, revision consistency, provenance completeness, and independence claims.

## 1. Raw submission

Source artifact: `RECEIVED_BIR1A_2026-09-03_RAW.md`

The artifact is explicitly marked `RAW BLIND EVIDENCE — NOT ADJUDICATED` and records prior Genesis exposure and relationship to the research operator as `unknown`. Therefore no L4/material external-independence claim is admissible from the artifact alone.

## 2. Challenge identity

The participant reported revision:

`49c575c69ed6d2194ec1e7b0660691b4a4e73c4e`

That revision exists and is a documentation commit. The exact `challenge-v2.json` content at that revision was fetched independently and matches the current frozen IR-V2 challenge content.

The declared challenge content SHA-256 is:

`03b25456a1ad0b40272daa1ca633910855433cfdce6ece8d0cf9e3352cd7ef1b`

The current challenge artifact is also bound to that same content digest by the active replication documentation. Git blob SHA-1 must not be confused with this content SHA-256.

**Result:** challenge identity consistent.

## 3. Provenance

Known:

- participant id: `ai-assistant-copilot-sdk-vscode`;
- runtime: VS Code Copilot SDK;
- execution timestamps are supplied;
- challenge revision and content digest are supplied.

Unknown:

- exact model/provider;
- exact runtime version;
- solver artifact digest;
- configuration digest;
- prior private-target exposure;
- relationship to the research operator;
- independently controlled execution environment.

**Result:** provenance partial.

## 4. Independence adjudication

The submission came through a coordinator conversation and explicitly does not establish independent control. A separate process or model interface is not, by itself, sufficient for material independence.

Therefore the only defensible current classification is:

`UNDETERMINED`

It must not be promoted to `MATERIAL_INDEPENDENCE_CONFIRMED` without corroborating evidence for the evidence path and operator relationship.

## 5. Semantic status

The submission reports a six-dimension basis and identifies several challenge under-specification issues. Those are preserved as candidate research evidence, but this audit does not compare them with any private target hypothesis and does not score agreement.

The submission's criticism that the challenge is under-specified for formal minimality is methodologically relevant and should be preserved independently of whether its basis converges with another result.

## 6. Red-team findings

1. **Revision spoofing:** resolved for the supplied revision because the revision exists and the challenge bytes at that revision were independently fetched.
2. **Digest confusion:** resolved by distinguishing Git commit/blob identifiers from content SHA-256.
3. **Process-independence fallacy:** not resolved; separate runtime does not establish material independence.
4. **Provider opacity:** unresolved because exact model/provider is not exposed.
5. **Prior-exposure uncertainty:** unresolved.
6. **Operator-control uncertainty:** unresolved.
7. **Pre-comparison contamination:** raw record states it was produced before comparison, but the delivery path alone cannot prove absence of hidden exposure.

## 7. Decision

The submission is retained as:

`RAW_BLIND EVIDENCE — CHALLENGE INTEGRITY VERIFIED — PROVENANCE PARTIAL — MATERIAL INDEPENDENCE UNDETERMINED — NOT ADJUDICATED`

It is valid to use for protocol testing, challenge critique, and candidate counterexample analysis. It is **not** valid as material external corroboration until the independence gate is separately satisfied.

## 8. Next action

Do not alter the frozen IR-V2 challenge in response to this submission. If a stronger independent execution is sought, use the active IR-V2 public call and obtain the missing provenance/independence evidence before semantic comparison.
