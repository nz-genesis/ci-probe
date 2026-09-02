# Blind Factorization Verification Contract

## Purpose

This directory defines a public, Genesis-agnostic mechanism for semantic factorization checks. It is infrastructure for an external reviewer or independently implemented solver; it is **not Genesis evidence by itself**.

## Lineage and evidence-counting boundary

BFV and the repository's `independent-replication/` (IR) mechanism are **not independent evidence sources from each other**. They were created inside the same project/repository lineage and address overlapping semantic questions with different public encodings and verifier contracts.

Repository chronology also places the IR mechanism before BFV. BFV is therefore treated as an alternate/control factorization surface, not as a second independent replication simply because it is stored under a different directory or uses different corpus identifiers.

For evidence counting:

- one external solver run over BFV and one over IR are not automatically two independent confirmations if the solver/evidence path is materially shared;
- a BFV result may still provide useful robustness, encoding-sensitivity, leakage, or counterexample evidence;
- material independence is adjudicated from the participant/evidence path, not from directory, protocol, prompt, or corpus name;
- the active public reconstruction challenge is maintained under `independent-replication/`; BFV remains a bounded control surface unless a separately governed study explicitly assigns it another role.

## Independence boundary

The participant receives only a frozen neutral obligation corpus and submission schema. The corpus must not expose the current Genesis primitive labels or a target factorization. The participant first derives anonymous factors and their obligation coverage. Only after submission may a private adjudicator compare the result with the current Genesis candidate.

A submission is not materially independent if the solver is seeded with the seven Genesis labels, the current factorization, acceptance examples authored from the target, or a prompt that asks it to reproduce the known answer.

## Required stages

1. Freeze the neutral corpus and record its digest.
2. Give the corpus to an independent mechanism without the candidate basis.
3. Require anonymous factorization before any adjudication.
4. Preserve the raw submission unchanged.
5. Independently normalize and compare the submission with the current candidate.
6. Run removal/composition and counterexample checks on the submitted factors.
7. Preserve disagreements and inconclusive outcomes.
8. Publish only the generic execution evidence; keep private semantic witnesses and adjudication material in the private Genesis repository.

## Valid outcomes

- `REPLICATED`: independent factorization supports the same bounded distinctions and finds no smaller normalized basis under the declared contract.
- `COUNTEREXAMPLE`: an independently derived irreducible obligation is not covered by the current candidate.
- `DISAGREEMENT`: material semantic disagreement remains unresolved.
- `BLOCKED`: no genuinely independent mechanism was available.

## Non-claims

A passing public workflow proves only that the generic verifier executed and its bounded assertions passed. It does not prove Genesis minimality, universality, canonical status, or independence from the IR lineage.
