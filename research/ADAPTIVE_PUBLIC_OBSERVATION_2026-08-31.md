# Adaptive Public Observation — 2026-08-31

**Status:** EXPERIMENTAL / EXECUTABLE / LOCAL VERIFICATION PENDING / HOSTED-CI PENDING

## Global Purpose
The Genesis Global Purpose remains unchanged. This bounded probe does not change Purpose, identity, canonical ontology, or architecture.

## Current goal
Test whether private-only mutations remain observationally indistinguishable when the external observer can choose later queries from earlier public observations.

## Non-duplication
P190 tests minimal private→public correspondence. P196/P197 cover direct/nested derived-field behavior and authorization-dependent publication. This probe changes the observation model: the observer is adaptive and constructs a transcript from sequential queries. It therefore tests a distinct side-channel boundary rather than repeating direct projection checks.

## Model
The state contains public status/version and private secret/score. The safe query interface exposes only declared public semantics. An adaptive observer first asks for `summary`; if it observes a ready state, it asks for `detail`. The adversarial interface leaks a private-score-derived bit only on the second query.

## Expected bounded result
Safe transcripts for states differing only in private data must be identical. Public semantic mutations must remain observable. The adversarial interface must be distinguishable under the same adaptive strategy, demonstrating that a direct one-shot projection check can miss an adaptive leak.

## Red Team
The probe attacks:
1. private-only mutation under sequential observation;
2. public mutation erasure;
3. a private-derived leak activated only after an earlier observation;
4. false assurance from equality of the first observation alone.

## Limits
This does not prove cryptographic noninterference, arbitrary adaptive side-channel resistance, timing/power/traffic-channel security, authorization completeness, or correspondence to real private Genesis state. It is a bounded deterministic semantic model.

## Primitive reduction
No new Genesis primitive is justified. Adaptive observation is treated as an observation pattern/constraint over State, Authority, Evidence and Projection behavior.

## Verification gate
The exact committed executable must be independently reproduced locally. Hosted CI may only be reported after the exact run is associated with the resulting commit and its completed conclusion is re-fetched from GitHub. A tool-returned write SHA or workflow-file presence is insufficient.

## Omission gate
If this probe passes, remaining boundaries include real private Genesis correspondence, richer adaptive/derived dependency graphs, canonical private CI, and other external-realization/irreversible-effect gaps already recorded by Genesis. No broader claim is inferred from this bounded test.
