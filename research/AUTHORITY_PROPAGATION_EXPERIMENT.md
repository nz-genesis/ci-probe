# Authority propagation delay experiment

## Question

When authority updates propagate with delay and multiple current observations disagree, can the reduced representation preserve safety and epistemic distinctions without introducing a new authority or execution primitive?

## Competing hypotheses

- **H1 — derived state is sufficient:** freshness and causal-order constraints applied to evidence yield the necessary authority classification.
- **H2 — propagation requires a primitive:** distributed propagation itself is an irreducible semantic primitive.
- **H3 — optimistic stale authorization is acceptable:** recent-enough-looking authorization may be admitted even when its evidence is stale or absent.

## Bounded model

Observations contain:

- source;
- authority classification;
- event time;
- observation time.

The decision context contains:

- realization time;
- freshness bound;
- human approval;
- irreversibility.

An observation is eligible only when its event precedes its observation and its observation is sufficiently fresh at realization.

## Scenarios

1. fresh authorization;
2. stale authorization after propagation delay;
3. current revocation despite human approval;
4. concurrent current authorized/revoked observations;
5. pending human approval at an irreversible boundary;
6. late revocation after a prior authorized observation;
7. late authorization after a prior revoke;
8. malformed causal ordering.

## Observed result

The same reduced vocabulary can classify the scenarios:

```text
fresh valid evidence      → AUTHORIZED
stale / unusable evidence → UNKNOWN
current revoke            → REVOKED
current disagreement      → CONFLICTING
pending human decision    → PENDING admission state
```

The model blocks irreversible admission for REVOKED, UNKNOWN and CONFLICTING. Human approval does not override a current revocation or missing authority evidence.

Late evidence changes the reconciled epistemic state but is not treated as retroactive proof that an already observed effect never occurred.

## Primitive-removal result

No dedicated `AuthorityPropagation`, `AuthorityUncertainty`, `DelegationEngine`, `Execution`, `Action`, or `HITL` primitive is required by this bounded model.

Propagation delay is represented through the relationship between event time, observation time, freshness constraints and evidence state. Conflict is derived from concurrently eligible evidence.

## Red Team targets

- Treating stale AUTHORIZED evidence as current authorization.
- Treating missing evidence as REVOKED rather than UNKNOWN.
- Treating concurrent contradictory observations as silently authorized.
- Treating human approval as an authority freeze.
- Treating late evidence as proof of non-effect.
- Treating a useful classification enum as an ontology primitive.
- Confusing the deterministic model with real distributed-system behavior.

## Limitations

This is still a deterministic clean-room model. It does not prove behavior under real network partitions, Byzantine sources, physical effects, uncertain clocks, consensus protocols, crash/recovery windows, or real-world authority/legal semantics.

## Public boundary

This repository contains generic executable experiments only. No private Genesis architecture, credentials, private datasets, internal endpoints or canonical decisions are included.
