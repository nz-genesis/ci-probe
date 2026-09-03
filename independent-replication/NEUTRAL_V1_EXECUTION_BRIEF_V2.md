# Neutral Clean-Room Execution Brief V2

**Status:** ACTIVE EXECUTION BRIEF / NOT SEMANTIC GUIDANCE
**Purpose:** obtain a materially independent reconstruction of a semantic basis from the frozen neutral discriminator corpus.

## 1. Participant-facing task

You are given a frozen corpus of opaque A/B pairs and a representation contract. Your task is to independently determine the semantic distinctions required to represent the differences in the corpus.

Do not assume a predefined ontology, category list, target basis, project architecture, or preferred answer. You may conclude that the corpus is incomplete, that a distinction is composite, that a smaller or larger factorisation is appropriate, or that the stated representation contract is insufficient.

For every proposed basis element:

1. define its semantic interpretation;
2. identify at least one case in which its semantic force varies independently;
3. attempt removal;
4. attempt merge with plausible neighboring elements;
5. attempt split if the element may contain independently variable coordinates;
6. inspect whether relations, attributes, metadata, predicates, or carrier structure are hiding semantic force;
7. test temporal validity, concurrency/partial order, epistemic status, normative/technical distinction, identity continuity, uncertainty/failure, and external-effect distinction where the corpus requires them.

Do not optimize for a small number of names. Optimize for the smallest defensible factorisation under the supplied representation contract while preserving all declared distinctions.

## 2. Exact inputs

Use exactly these frozen public inputs and no substitute revisions:

- Challenge: `independent-replication/neutral-v1/challenge.json`
- Representation contract: `independent-replication/neutral-v1/representation-contract-v2.md`

Before semantic work, compute and record:

- exact Git commit used;
- challenge byte size and SHA-256;
- representation-contract byte size and SHA-256;
- this execution brief byte size and SHA-256.

If any expected input is missing or its bytes differ from the frozen revision you were instructed to use, abort before semantic analysis.

## 3. Blindness / contamination boundary

Do not inspect or use:

- private material belonging to the corpus owner;
- any candidate ontology or primitive list from the corpus owner;
- prior participant results;
- prior interpretations of this challenge;
- hidden evaluator labels;
- target-vocabulary lists supplied after execution begins;
- any unpublished decision criteria intended to favor a particular answer.

If you already know material information that could bias the reconstruction, declare the exposure before analysis. Do not attempt to compensate by guessing.

## 4. Required raw report

Produce one standalone raw report containing:

A. execution metadata;
B. exact input digests;
C. independence/exposure declaration;
D. your independently derived semantic basis;
E. case-by-case mapping for all 36 pairs;
F. removal analysis for every proposed basis element;
G. merge/split analysis;
H. anti-laundering analysis;
I. temporal/causal/concurrency analysis;
J. epistemic and normative analysis;
K. external-effect analysis;
L. identity/carrier analysis;
M. explicit counterexamples against your own basis;
N. omitted-domain / corpus-limit analysis;
O. final bounded verdict and unresolved questions.

Do not compare your result with any other participant, private material, or target ontology before freezing this raw report.

## 5. Freeze and provenance

After completing the report:

1. save the exact raw bytes;
2. compute SHA-256 and byte count;
3. record execution start/end times;
4. record model/provider and exact runtime/version if available;
5. record whether prior exposure exists;
6. record relationship to the corpus owner/operator;
7. record prompt-contract SHA-256;
8. create a cryptographic commitment to the raw report before any comparison if your environment supports a reproducible commitment mechanism;
9. do not edit or regenerate the raw report after computing its digest;
10. return the exact frozen artifact and its digest for repository publication.

If repository write access is available, publish the exact frozen artifact in a new evidence-only branch. Commit only the artifact unless a separate governance instruction says otherwise. Verify the remote branch and committed bytes after push.

## 6. Semantic comparison timing

Do not perform comparative adjudication against prior participants or any target basis before the raw report is frozen and its digest recorded.

After freeze, comparison may be performed only as a separate clearly labelled adjudication artifact. The raw report must remain unchanged.

## 7. Epistemic boundary

Your result is evidence about the declared corpus and representation contract. It is not a proof of a globally minimal ontology and must not be described as one.

A disagreement with another reconstruction is valid evidence. Do not force convergence.
