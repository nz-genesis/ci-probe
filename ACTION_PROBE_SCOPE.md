# Generic Action Probe — Public Scope

This document defines the executable experiment in this repository. It is deliberately implementation- and project-agnostic.

## What is tested

The probe tests a generic consequential-action lifecycle:

```text
contract
  → admission
  → execution
  → observation
  → outcome verification
  → trace
```

It also tests two safety properties:

- capability and authority are independently required for admission;
- an unknown execution state is not treated as safe to retry.

## What is deliberately not tested here

The probe does not define, encode, or reveal any private project's ontology, architecture, prompts, internal tools, private topology, unpublished research, canonical state, or authority model.

The strings used by the fixture (`fixture-target`, `fixture-write`, `test-authority`) are synthetic and have no external meaning.

## Interpretation boundary

A passing test establishes only the behavior of this generic model and its deterministic fixture. It is not proof of a private system's architecture or behavior.

A private research process may use the public observation as substrate evidence, but must independently establish:

- applicability;
- scope;
- provenance;
- limitations;
- alternative explanations;
- downstream implications;
- whether the result is sufficient to support an architectural decision.

## Required public invariants

1. No private credentials or external side effects.
2. No network dependency.
3. No dependency on a private repository.
4. No automatic write-back to any private repository.
5. No private-to-public synchronization path.
6. Deterministic tests suitable for clean-room reproduction.

## Research mapping

This public probe is an experimental substrate only. Its observations may be cited from the private research lane as evidence about generic execution semantics, without treating the public repository as authoritative Genesis architecture.
