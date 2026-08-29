# Primitive Removal K2 — Invariant Preservation

## Question

Does removing a candidate dimension merely lose a representation, or does it make a required semantic invariant impossible to preserve without covertly reintroducing that candidate as a primitive?

## Competing hypotheses

- H1: candidate is irreducible because its invariant cannot survive removal.
- H2: candidate is representational/compositional; distinction and invariant can survive generic representation.
- H3: a fixture can appear reduced while covertly reintroducing the candidate under another name.

## Method

For each of the seven current research candidates — State, Transition, Capability, Authority, Observation, Evidence, Constraint — construct a minimal pair differing only along that dimension. Test both observable distinction and the relevant invariant. The representation treats the removed dimension as generic data rather than as a dedicated type.

K2 is intentionally stronger than K: information-preserving re-encoding alone is insufficient evidence for primitive reduction. A successful reduction must preserve the invariant as well.

## Current bounded result

The executable fixture preserves all seven distinctions in generic attributed data. The constraint case additionally demonstrates that merely retaining the fact that a cardinality bound exists is not enough: the actual invariant must be evaluated. The one-effect case satisfies `at-most-one`; the two-effect case violates it.

This is evidence against using simple projection collision as a primitive criterion. It is **not** proof that all seven candidates can be removed from Genesis.

## Red-team requirements

The following remain open and are not claimed solved by this fixture:

1. covert reintroduction of a candidate under another label;
2. invariant enforcement versus invariant description;
3. heterogeneous domain coverage;
4. authority and evidence trustworthiness;
5. distributed causal/temporal semantics;
6. external physical effects;
7. persistence/recovery across crashes.

## Public boundary

This repository contains only generic executable experiments. No private Genesis architecture, credentials, internal endpoints, datasets, or canonical decisions are included. Interpretation belongs to private `genesis-lab`.
