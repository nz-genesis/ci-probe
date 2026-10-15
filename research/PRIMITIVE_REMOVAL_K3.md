# Primitive Removal K3 — Heterogeneous Invariant Preservation

## Scope

K3 extends K2 from seven isolated minimal pairs to seven materially different domains. It deliberately uses generic data records and independently named invariant predicates rather than candidate-specific classes.

## Domains

- research → Evidence
- software → State
- governance → Authority
- robotics → Capability
- distributed systems → Transition
- recovery → Observation
- self-evolution → Constraint

## Bounded result

The executable fixture preserves an independently stated invariant for each case while representing the candidate dimension as data rather than a dedicated candidate-specific type.

This strengthens the K/K2 methodological result: representational distinguishability and an independently checked invariant can coexist without requiring a candidate-specific type in the clean-room fixture.

It still does **not** prove that any Genesis candidate can be removed. The invariants are intentionally small and the domains are illustrative rather than complete implementations.

## Red Team

Open risks:

1. invariant predicates are deliberately simple;
2. generic data may still hide an implicit ontology;
3. no distributed clock/causal model is implemented;
4. no physical effect is implemented;
5. no adversarial authority source is implemented;
6. no crash-persistent substrate is implemented;
7. workflow execution must be verified before CI evidence is claimed.

## Boundary

This is clean-room generic experiment material only. It contains no private Genesis architecture, credentials, internal endpoints, private datasets or canonical decisions.
