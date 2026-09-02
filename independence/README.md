# Blind Factorization Verification Contract

## Purpose

This directory defines a public, Genesis-agnostic mechanism for materially independent semantic factorization checks. It is infrastructure for an external reviewer or independently implemented solver; it is **not Genesis evidence by itself**.

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

A passing public workflow proves only that the generic verifier executed and its bounded assertions passed. It does not prove Genesis minimality, universality, or canonical status.
