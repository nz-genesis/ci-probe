# Generic Action Probe — Public Scope

This is a public, project-agnostic executable experiment. It contains no private project ontology, architecture, prompts, internal tools, private topology, unpublished research, credentials or datasets.

## Bounded properties

- Capability and authority are independently required for admission and are rechecked against the exact admitted values at dispatch.
- The executor cannot silently change the admitted target or operation, including identifiers containing delimiters.
- Executor completion is not equivalent to verified external state.
- An unknown execution state is not safe to retry without reconciliation, including an internally inconsistent record with zero attempts.
- Reconciliation classifies an already-attempted execution without executing it again.
- A failed status alone does not authorize a new operation retry; effect certainty must explicitly confirm no effect, and a new identity/fresh admission is still required.
- The scenario matrix distinguishes pre-effect failure, possible effect, partial effect, unknown and unresolved reconciliation.
- The dedicated scenario workflow runs both the root generic action-contract tests and the full scenario-matrix test module. Its push trigger is path-scoped to the files it owns, it retains manual dispatch, and its checkout action is pinned to actions/checkout v7.0.1 (full commit SHA, Node 24 runtime).

## Explicit limitations

The probe has no persistence, network, provider integration, external side effect or real authorization authority. Its fixtures model inputs and observations; they are not an actual provider or computer executor. It does not claim exactly-once delivery, distributed consensus, physical-world safety, durability or security of arbitrary external executors. Other repository probes for late evidence, artifact closure, external-effect recovery and evidence-scope binding are separate experiments; their results are not silently combined into one proof.

A passing run establishes only the behavior of these generic models and deterministic fixtures. It is not proof of any private system's architecture or behavior.

## Required public invariants

1. No private credentials or external side effects.
2. No network dependency or private-repository dependency.
3. No automatic write-back to any private repository.
4. No private-to-public synchronization path.
5. Deterministic tests suitable for clean-room reproduction.
6. Public code remains Genesis-agnostic.

## Evidence flow

    public generic experiment
            ↓
    public observation
            ↓
    private review / applicability check
            ↓
    private evidence record

Private artifacts must never be copied into this repository merely to make an experiment easier to run.
