# Temporal + Authoritative Evidence — Bounded Probe

**Date:** 2026-08-31
**Status:** EXPERIMENTAL / EXECUTABLE / HOSTED-CI PENDING

## Question
Can temporal validity, source authority and contradiction handling be represented without introducing a new Genesis epistemic primitive?

## Scope
This probe extends the previous evidence-grounded cognitive synthesis discriminator. It does not repeat artifact replay or generic environment tests.

## Model
A source has:

- stable source id;
- authority rank;
- validity interval;
- signed/declared facts in the bounded model.

Claim admission requires a currently valid supporting source and rejects unsupported claims. A valid contradictory source of equal or higher authority blocks admission; stale contradictions do not.

## Cases
Eight bounded cases cover current evidence, stale contradiction, lower-authority contradiction, future evidence, stale-only evidence, equal-authority contradiction, and unsupported claims.

Expected executable result: `TEMPORAL AUTHORITATIVE EVIDENCE: 8/8 PASS`.

## Red Team
- Stale-source poisoning: stale source must not veto or establish a current claim.
- Future-source leakage: future-valid source must not establish a claim before its validity interval.
- Authority inversion: lower authority contradiction must not silently override higher authority.
- Equal-authority disagreement: ambiguity must block claim admission rather than invent resolution.
- Unsupported claim: rejected.
- New epistemic primitive laundering: none; temporal validity and authority are properties/constraints over evidence admission in this bounded model.

## Limits
This does not establish real source authenticity, cryptographic trust, legal authority, truth of a source, or universal conflict-resolution policy. Those require separate evidence.

## Decision
No new Genesis primitive is justified by this bounded test. Temporal validity is modeled as a constraint over evidence; authority remains an authority/admission responsibility; contradiction is a verification/admission condition.

## Next discriminator
Test evidence authenticity/equivocation and then irreversible external effect with independent world observation. Do not repeat this probe without changing the semantic discriminator.
