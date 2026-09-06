# External Agent Task — Challenge-Origin Independent Construction v1

**Status:** `PREPARED / NOT AN IR-V3 MUTATION`
**Purpose:** create a fresh independent measurement surface whose obligation corpus is generated without access to the target system, its candidate ontology, private research, or prior target adjudication.

## Critical boundary

This task is **not** a semantic reconstruction of IR-V3 and must not modify `challenge-v3.json`.

The generator MUST NOT access:

- the private Genesis repository;
- any private research or target ontology;
- the seven-element candidate or any equivalent target basis;
- prior Genesis adjudication;
- private reduction maps;
- previous participant results.

Only public, external domain sources and this task contract may be used.

## Role

You are the **challenge generator**, not the adjudicator.

Your task is to construct a bounded set of semantic contrast cases from independently selected public domain material, then freeze the cases before any target interpretation is available.

Do not attempt to make the cases fit a presumed ontology.
Do not produce a target basis.
Do not use a supplied list of semantic dimensions.

## Source requirements

Use at least 6 materially different public domains and at least 2 independent source families per domain where practical. Suitable source families include technical standards, scientific/engineering descriptions, operational procedures, formal governance specifications, and public domain documentation.

For each case preserve source provenance sufficient for later audit. The source is evidence for the scenario construction, not evidence for any semantic basis.

## Case-generation rule

For each selected domain:

1. identify a concrete distinction that matters in the source domain;
2. construct two or more minimally different world descriptions whose observable consequences differ on that distinction;
3. remove domain-specific jargon where doing so does not destroy the distinction;
4. do not name an abstract semantic factor;
5. do not write requirements such as “preserve authority”, “preserve evidence”, “preserve capability”, or other ontology-like labels;
6. express the requirement as a concrete consequence: what must remain distinguishable, reconstructable, or decidable;
7. include adversarial variants where an implementation can appear equivalent while hiding the distinction in an identifier, relation, metadata field, or unspoken assumption;
8. record what source material motivated the distinction, but keep that genealogy separate from the frozen participant-facing case text.

## Anti-target-loading requirements

The generator MUST explicitly audit its own cases for:

- candidate vocabulary leakage;
- one-to-one mapping between case families and an assumed basis;
- overuse of one semantic pattern;
- hidden evaluator dictionaries;
- requirements that already name the desired factor;
- case selection designed merely to reproduce a known factorization.

The public participant-facing challenge must contain only the frozen cases, neutral instructions, and the minimum provenance needed to reproduce the case construction. The generator's rationale and source-to-case mapping should be frozen separately before participant reconstruction.

## Freeze protocol

Before any comparison with a target hypothesis:

1. freeze exact challenge bytes;
2. compute content SHA-256;
3. preserve source genealogy;
4. preserve generator provenance and execution environment;
5. create commitment over the challenge digest and generator run ID;
6. publish commitment before revealing the generator rationale or any target comparison;
7. only then make the participant-facing challenge available.

## Participant stage

A **separate** external participant must later reconstruct the semantic basis from the frozen challenge without seeing:

- generator rationale;
- source-to-case mapping;
- target hypothesis;
- Genesis research;
- prior factorization results.

Participant execution requires its own raw freeze, commitment/reveal, provenance and material-independence adjudication.

## Admissible outcomes

The participant may report:

- a finite basis;
- a smaller or different basis;
- irreducible residue;
- omitted obligations;
- challenge under-specification or target-loading;
- H4/no-finite-basis;
- inconclusive reconstruction.

No outcome is considered a failure merely because it disagrees with another basis.

## Why this exists

This task addresses a measurement-instrument problem exposed by the IR-V3 apparatus audit: an externally independent participant can still be given a challenge whose obligation selection was not independently generated. Participant independence and challenge-generation independence are therefore separate gates.

This document is a prepared future route. It does not establish any semantic result and does not replace the frozen IR-V3 campaign.
