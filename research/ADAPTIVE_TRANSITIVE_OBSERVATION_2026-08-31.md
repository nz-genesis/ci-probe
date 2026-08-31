# Adaptive Transitive Observation — 2026-08-31

## Status

`EXPERIMENTAL / LOCAL VERIFIED / HOSTED-CI PENDING / NOT CANONICAL`

## Question

Does private-only state remain observationally noninterfering when an adaptive public observer can observe a first response, then encounter a multi-hop derived public response whose value depends on an intermediate derived field?

## Distinction from prior work

P204 established that one-shot projection equality is insufficient under adaptive observation. This probe changes the discriminator: the private value is not exposed directly in the first or second response; it contaminates an intermediate derived value which is then transformed again into a later observable response. Existing P196/P197 derived-field and authorization-dependent publication probes do not establish this adaptive multi-hop transcript property.

## Model

State contains `public_status`, `private_score`, and `private_note`.

Safe implementation derives all observable values from declared public semantics. The red-team implementation derives an intermediate `high/low` value from `private_score`, then hashes that intermediate value into a later public response. The first response remains identical across the private mutation, deliberately defeating a shallow first-response check.

## Local verification

The exact committed executable was independently reproduced before reporting and returned:

`ADAPTIVE TRANSITIVE OBSERVATION: 6/6 PASS`

The six checks cover:

1. private-only mutation leaves the safe transcript unchanged;
2. public mutation remains observable;
3. the adversarial transcript differs under private mutation;
4. the first adversarial response is identical, proving the shallow check is insufficient;
5. the second response reveals the derived leak;
6. the later transformed response preserves the distinguishability.

## Red Team

- shallow first-response equality;
- direct private-field exposure;
- indirect private→derived→public leakage;
- adaptive path selection after an apparently safe first response;
- false promotion from one-hop projection equality to multi-hop noninterference.

## Finding

A bounded adaptive transcript check should account for transitive derived dependencies, not only direct private-to-public mappings. A private-only mutation can remain hidden at the first observation while becoming observable through a later derived response.

## Primitive reduction

No new Genesis primitive is justified. The result is expressible through existing state, observation, constraints, evidence and projection/derivation semantics.

## Limits

This is a small authored clean-room model. It does not establish arbitrary graph depth, arbitrary side channels, cryptographic noninterference, real private Genesis correspondence, authorization completeness, or canonical private CI.

## Hosted CI

Workflow file exists and was re-fetched after write. Hosted execution is not claimed until an exact run associated with the resulting commit is independently inspected and its completed conclusion verified.
