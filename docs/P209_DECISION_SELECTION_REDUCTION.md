# P209 — Decision / Selection Reduction

## Question

Can decision, selection, policy, and preference be represented using the current seven-element Genesis candidate basis without introducing a new semantic primitive?

Basis:

- State
- Transition
- Capability
- Authority
- Observation
- Evidence
- Constraint

## Bounded scenarios

- select among multiple admissible transitions using an explicit constraint/criterion;
- change the admissible choice by changing state/constraint;
- represent policy change as a protected state transition;
- tie/ambiguity does not become success automatically;
- unauthorized preference cannot expand authority;
- observation is not decision;
- UNKNOWN is not success;
- evidence of one realization does not become authority for another;
- conflicting authority is resolved by authority/constraint, not by preference laundering;
- malformed candidate fails closed;
- primitive reduction check.

## Falsifier

P209 is falsified if a decision/selection operation requires a semantic primitive outside the seven-element basis, or if policy/preference can silently widen authority, constraints, or execution scope.

## Evidence protocol

The cumulative CI Probe checks out the exact triggering SHA, verifies `HEAD == GITHUB_SHA`, executes the P209 probe after the already-closed cumulative probes, and preserves the existing hosted evidence chain.

A hosted PASS is execution evidence for the probe, not proof of canonical Genesis semantic correctness.
