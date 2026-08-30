# Temporal + Authoritative Evidence — Bounded Probe

**Date:** 2026-08-31
**Status:** EXPERIMENTAL / EXECUTABLE / LOCAL PASS / HOSTED-CI PENDING

## Question
Can temporal validity, source authority and contradiction handling be represented without introducing a new Genesis epistemic primitive?

## Scope
This probe extends the evidence-grounded cognitive synthesis discriminator. It does not repeat artifact replay, generic environment tests, or the existing atomicity/equivocation/provenance research.

## Model
A source has a stable source id, authority rank, validity interval, and declared facts in the bounded model. Claim admission requires a currently valid supporting source. A currently valid contradictory source of equal or higher authority blocks admission; stale and future sources are outside the current evidence set.

## Cases
Eight bounded cases cover current evidence, stale contradiction, lower-authority contradiction, future evidence before and after validity, stale-only evidence, equal-authority contradiction, and unsupported claims.

## Local execution
The exact committed probe logic was independently reproduced and executed in a clean Python environment. Result:

`TEMPORAL AUTHORITATIVE EVIDENCE: 8/8 PASS`

Hosted CI has not been independently observed as completed, so hosted PASS is not claimed.

## Red Team
- Stale-source poisoning: stale source must not veto or establish a current claim.
- Future-source leakage: future-valid source must not establish a claim before its validity interval.
- Authority inversion: lower authority contradiction must not silently override higher authority.
- Equal-authority disagreement: ambiguity must block claim admission rather than invent resolution.
- Unsupported claim: rejected.
- New epistemic primitive laundering: none; temporal validity and authority are properties/constraints over evidence admission in this bounded model.

## Limits
This does not establish real source authenticity, cryptographic trust, legal/organizational authority, truth of a source, Byzantine equivocation, or a universal conflict-resolution policy.

## Decision
No new Genesis primitive is justified by this bounded test. Temporal validity is modeled as a constraint over evidence; authority remains an authority/admission responsibility; contradiction is a verification/admission condition.

## Next discriminator
Do not repeat this probe. Existing repository research already covers bounded equivocation/provenance. Prioritize either private→public semantic correspondence or irreversible external effect with independent world observation.
