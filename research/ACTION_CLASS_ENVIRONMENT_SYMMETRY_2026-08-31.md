# Bounded Action-Class × Environment Symmetry

**Date:** 2026-08-31
**Status:** EXPERIMENTAL / EXECUTABLE / HOSTED-CI PENDING

## Question
Does environment symmetry survive when the action class changes, rather than only when the environment changes?

## Prior-art boundary
The earlier environment-symmetry probe tested one state-mutation action across eleven realization classes. This pass deliberately changes the semantic action class while retaining the same realization matrix. It does not repeat replay, ACK, coordinator, partition, or authority-history experiments.

## Matrix
Four action classes × eleven realization classes = 44 bounded executions:

1. state mutation
2. artifact creation
3. observation-only action
4. protected/meta change

Realization classes: own state, local process, filesystem/storage, attached hardware, local network, remote system, another Genesis, Internet, human, physical environment, simulated environment.

## Contract
`operation_id + authority + capability + version + payload`

No environment selector is present in the contract.

## Local validation target
The executable must report `MULTI-ACTION ENVIRONMENT SYMMETRY: 44/44 PASS`.

## Red Team
- environment-specific field laundering: rejected by contract inspection;
- authority bypass: denied contract must fail for every matrix cell;
- stale version bypass: stale contract must fail for every matrix cell;
- observation spoofing: verification reads realization state after execution;
- protected-change downgrade: protected change only accepts the declared target version;
- artifact-only false positive: artifact class requires observed persisted artifact;
- observation mutation leakage: observation-only class must not mutate state;
- overclaim: realization classes are semantic surrogates, not real integrations.

## Decision rule
A local or hosted PASS supports only bounded action-class symmetry. It does not prove universal action/environment closure. A failure must identify the missing semantic dimension before any primitive is proposed.

## Omission gate
Still required: a materially different external/irreversible effect model; richer cognitive/artifact semantics; real private Genesis correspondence; cross-domain atomicity; Byzantine/equivocation; actual hosted execution; and independent case provenance from the Genesis functional-chain corpus.
