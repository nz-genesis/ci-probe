# IR-V3 Minimality Challenge — Proposal

Status: `RESEARCH PROPOSAL — NOT ACTIVE / NOT EVIDENCE`

## Purpose

IR-V3 is proposed as a successor experiment to IR-V2 for testing whether an independently derived semantic basis is **minimal under an explicit representation contract**, rather than asking an open-ended question about global ontology minimality.

IR-V2 remains frozen and must not be modified. This proposal does not invalidate IR-V2; it addresses a measurement limitation exposed by IR-V2.

## Why IR-V3 is needed

IR-V2 asks for the "smallest sufficient semantic basis" but does not fully define:

- the admissible representation language;
- what counts as one primitive/dimension;
- the equivalence relation between two bases;
- the reconstruction objective;
- the formal criterion for minimality.

Therefore IR-V2 can detect useful distinctions and counterexamples, but it cannot by itself establish a unique global minimum.

## Design principle

IR-V3 MUST test **relative minimality under a declared contract**, not pretend to prove implementation-independent absolute ontology minimality.

The public challenge MUST remain Genesis-agnostic and MUST NOT publish a target factorization.

## Proposed formal contract

A participant submits a basis B and a reconstruction mapping R for a frozen obligation corpus O.

A candidate is admissible only if every basis element is:

1. independently nameable without referring to a hidden target ontology;
2. semantically interpretable across the corpus;
3. non-opaque (it may not encode an arbitrary unrelated tuple under one label);
4. composable with the declared representation operators;
5. sufficient to reconstruct every mandatory obligation;
6. falsifiable by a removal test.

### Sufficiency

For every mandatory obligation `o ∈ O`, the submitted representation must reconstruct all distinctions explicitly required by `o` without adding information not present in the submitted representation.

### Removal criterion

For every basis element `b ∈ B`, construct `B - {b}` while preserving the same representation operators and admissibility rules. If at least one mandatory obligation can no longer be reconstructed, `b` is removal-necessary for that submission.

### Redundancy criterion

If two basis elements can be merged into one admissible element without losing any mandatory distinction and without introducing an opaque composite, the submission is non-minimal under the contract.

### Splitting criterion

A single basis element that contains independently removable semantic parts is a composite and MUST be split if those parts can be independently named and used under the same representation contract.

### Equivalence criterion

Two submissions are equivalent only when each can reconstruct the same mandatory obligations and each maps to the other through admissible rename/merge/split transformations that preserve all required distinctions. Mere numerical agreement in basis size is not equivalence.

## Anti-trivialization constraints

The following are prohibited as basis elements:

- universal catch-all primitives such as `Everything`;
- arbitrary opaque tuples encoding several unrelated dimensions;
- labels whose only justification is that they make a case pass;
- implementation-specific classes, services, databases, APIs, agents, or runtimes unless the obligation itself explicitly requires an implementation property;
- a single unrestricted relation whose payload can encode the entire corpus;
- target labels or terminology supplied by an adjudicator.

The challenge MUST explicitly state these constraints so that "one primitive that stores everything" is not accepted as a minimal solution.

## Required participant output

The active challenge should require:

1. basis elements with operational semantic definitions;
2. one mapping for every mandatory obligation;
3. removal test for every basis element;
4. at least three merge/split analyses;
5. at least three adversarial counterexamples;
6. explicit uncertainty and challenge criticism;
7. execution provenance;
8. a statement of prior target exposure.

## Evaluation

The public verifier should perform only deterministic structural checks:

- schema validity;
- corpus digest;
- complete obligation coverage;
- unique basis identifiers;
- unique mapping identifiers;
- removal-analysis coverage;
- forbidden opaque/catch-all marker detection where mechanically decidable;
- canonical submission digest.

Semantic minimality MUST remain a separate adjudication step. The public verifier MUST NOT claim to prove semantic minimality.

## Independent adjudication

A semantic reviewer receives the frozen submission only after the raw result is committed/frozen. The reviewer checks:

```text
Sufficiency
Removal necessity
Merge possibility
Composite/split validity
Counterexamples
Cross-domain consistency
Implementation independence
```

The reviewer must preserve `REPLICATED`, `COUNTEREXAMPLE`, `DISAGREEMENT`, and `INCONCLUSIVE` as distinct outcomes.

## Required comparison rule

IR-V3 results MUST NOT be counted as independent evidence merely because the participant used a different challenge version. Independence is a property of the participant/evidence path.

IR-V3 should preferably use a genuinely separate participant from the IR-V2 run, with no exposure to the prior result.

## What IR-V3 can establish

At most, a successful IR-V3 can establish that a submitted basis is minimal **under the declared corpus, representation contract, and adjudication criteria**.

It cannot establish that the basis is the globally minimal ontology for all possible systems or all possible representations.

## What remains open

- exact formal representation language;
- exact merge/split admissibility rules;
- formal equivalence algorithm versus bounded adjudication;
- corpus expansion and domain balance;
- whether a finite obligation corpus is sufficient for the intended Genesis claim;
- whether the experiment should compare several independently derived bases rather than one participant.

These must be resolved and Red-Teamed before IR-V3 becomes an active frozen challenge.
