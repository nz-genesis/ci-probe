# Generic Action Probe — Public Scope

This document defines the executable experiment in this repository. It is deliberately implementation- and project-agnostic.

## What is tested

The probe tests a generic consequential-action lifecycle:

```text
contract
  → admission
  → realization boundary
  → execution
  → observation / reconciliation
  → outcome verification
  → trace
```

The public probe tests these bounded properties:

- capability and authority are independently required for admission;
- the executor cannot silently change the admitted target or operation;
- executor completion is not equivalent to verified external state;
- an unknown execution state is not safe to retry without reconciliation;
- reconciliation classifies an already-attempted execution without executing it again;
- the same contract can be exercised by separate generic realizations without changing its semantic contract.

## What is deliberately not tested here

The probe does not define, encode, or reveal any private project's ontology, architecture, prompts, internal tools, private topology, unpublished research, canonical state, or authority model.

The strings used by the fixture (`fixture-target`, `fixture-write`, `test-authority`) are synthetic and have no external meaning.

The probe does not claim exactly-once delivery, distributed consensus, physical-world safety, causal attribution, or security of arbitrary external executors. Those are separate research questions requiring stronger evidence.

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
7. Workflow files are treated as executable public content and are included in boundary checks.
8. Public code remains Genesis-agnostic: no private ontology, architecture name, internal identifier, unpublished hypothesis, or canonical decision is required by the probe.

## Evidence flow

```text
public generic experiment
        ↓
public observation
        ↓
private review / applicability check
        ↓
private Genesis evidence
```

The reverse direction is not automated. Private Genesis artifacts must never be copied into this repository merely to make an experiment easier to run.

## Research mapping

This public probe is an experimental substrate only. Its observations may be cited from the private research lane as evidence about generic execution semantics, without treating the public repository as authoritative Genesis architecture.
