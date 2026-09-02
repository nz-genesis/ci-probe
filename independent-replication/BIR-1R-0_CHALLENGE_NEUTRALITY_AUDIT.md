# BIR-1R-0 — IR-V2 Challenge Neutrality Audit

**Date:** 2026-09-02  
**Status:** OPEN FINDING / NO CHANGE TO FROZEN IR-V2

## Finding

IR-V2 is operationally neutral in the sense that it does not name a supplied Genesis ontology or provide a candidate basis. However, its natural-language cases explicitly foreground several semantic distinctions that are also central to the intended research question.

Examples include:

- external result vs received signal;
- technical capability vs permission;
- attempted operation vs established external outcome;
- unresolved external outcome;
- concurrency without justified total ordering;
- continuity through transformation;
- historical circumstance despite equal present condition;
- time-dependent validity.

These statements are legitimate requirements for the challenge, but they can also prime a solver toward particular distinctions. Therefore the label `FROZEN_NEUTRAL_PUBLIC_CHALLENGE` must not be interpreted as proof that the wording is free from semantic priming.

## Classification

| Cue | Classification | Reason |
|---|---|---|
| External result vs received signal | Necessary operational requirement + priming risk | The case explicitly requires the distinction rather than merely describing an observation problem. |
| Capability vs permission | Necessary operational requirement + priming risk | The requirement names both concepts as distinct roles. |
| Attempt vs established external result | Necessary operational requirement + priming risk | Explicitly prevents collapsing action into effect. |
| Unresolved result | Necessary operational requirement | Needed to test representation of epistemic uncertainty after interaction. |
| Concurrency / no justified ordering | Necessary operational requirement | Tests whether representation invents unsupported order. |
| Continuity through transformation | Necessary operational requirement | Tests persistence across changing observable condition. |
| Historical circumstance with equal present condition | Necessary operational requirement | Directly tests whether present-state equality is sufficient. |
| Time-dependent validity | Necessary operational requirement | Directly tests temporal scope. |

## Consequence for BIR-1

BIR-1 remains valid as a **blind internal replication/control experiment**, but its result must not be interpreted as evidence that the participant independently discovered every highlighted distinction without prompting. The experiment can still test:

1. whether a solver can construct a coherent basis from the requirements;
2. whether it finds additional distinctions not foregrounded by the challenge;
3. whether it rejects unnecessary distinctions;
4. whether its minimality and counterexamples survive adversarial review.

## Required separation

Do **not** edit IR-V2 while BIR-1 is in progress. Any less-primed challenge must be a new immutable version (for example, IR-V3) with a separately recorded provenance and recruitment window.

## Stronger future control

A future challenge should, where feasible, describe observable scenarios and required reconstruction properties while minimizing names of candidate semantic distinctions. An independent challenge designer should review that wording before publication.

## Epistemic status

This document records a methodological limitation. It is not evidence for or against Genesis semantics and does not alter canonical Genesis architecture.
