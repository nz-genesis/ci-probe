# P388 — Selection-Conditioned Risk-Control Routing

**Status:** PUBLIC-SAFE EXECUTION PROBE / EXPERIMENTAL  
**Date:** 2026-10-07  
**Repository:** `nz-genesis/ci-probe`

## Purpose

P388 is a deliberately generic public execution contract derived from the private Genesis Decision Evaluation research. It tests whether a bounded selector can:

- calibrate an informative but imperfect score without using the test split;
- choose the maximum-retention threshold satisfying a held-out calibration risk bound;
- preserve a hard evidence-sufficiency gate;
- include error cost in route comparison;
- refuse to claim a statistical guarantee when its exchangeability assumption is not asserted.

It does **not** contain Genesis private corpus, labels, prompts, rationales, hidden oracle, architecture decisions or proprietary evaluator outputs.

## Why this is not P306/P307 duplication

P306 tests sufficient-control verification-count / wall-time trade-offs.

P307 tests provider-contract × retry/recovery control-cost interaction.

P388 adds a distinct discriminator: **selection-conditioned statistical risk control plus calibration/test separation and an explicit assumption boundary**. Its executable contract is not a replay of either prior probe.

## External methodological basis

2026 literature strengthens the need for this discriminator. LEC formulates selection-conditioned risk control and extends it to two-model routing under exchangeability and held-out calibration. A 2026 ACL study applies conformal calibration to LLM routing and reports distribution-free violation control under stated assumptions. These are external methodological references, not Genesis primitives or safety guarantees.

## Non-claims

A green P388 run proves only that the exact public artifact executed and its bounded assertions passed on the GitHub-hosted runner.

It does not prove:

- Genesis semantic correctness;
- production safety;
- universal superiority of calibrated routing;
- validity under distribution shift;
- correctness of any LLM judge;
- physical-world safety;
- Genesis primitive canonization.

## Required private correspondence step

After the exact public run, private Genesis research must re-fetch the exact commit, workflow run, job, steps and logs and assess correspondence to the private P1 mechanism without importing private corpus into the public repository.
