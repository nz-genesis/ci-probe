# P197 — Authorized Derived Public Semantics — 2026-08-31

**Status:** `EXPERIMENTAL / EXECUTABLE / LOCAL PASS / HOSTED-CI PENDING / NOT CANONICAL`

## Global Purpose
Глобальная цель Genesis остаётся неизменной; этот bounded pass не изменяет Purpose, identity или canonical ontology.

## Current goal
Проверить границу, на которой private information может легитимно влиять на public derived semantics: влияние допустимо только когда dependency явно объявлена частью public semantic contract и publication authority присутствует. Без declaration или authority private mutations должны оставаться observationally equivalent на public boundary.

## Non-duplication
P190 проверяет минимальную private→public correspondence; P196 проверяет nested noninterference и adversarial leakage. P197 добавляет materially different discriminator: authorized semantic dependency versus undeclared/unauthorized dependency, плюс observational equivalence across private states.

## Evidence
Executable: `authorized_derived_public_semantics.py`
Workflow: `.github/workflows/authorized-derived-public-semantics.yml`

Exact committed logic was independently reproduced in a clean Python environment and produced `AUTHORIZED DERIVED PUBLIC SEMANTICS: 8/8 PASS`.

## Red Team
- private mutation without declared dependency remains unobservable;
- declared dependency without publication authority remains unobservable;
- declared + authorized dependency intentionally changes public derived semantics;
- an adversarial implementation that ignores the contract and leaks the private score is detected;
- public semantic mutation remains observable independently of private state.

## Finding
Privacy/noninterference is not equivalent to "private data can never influence public output". A private value may become part of public semantics when the dependency is explicitly declared and authorized. The important boundary is contract + authority, not the private/public label alone.

## Primitive reduction
No new Genesis primitive is justified. The distinction composes State, Constraint/contract, Authority and Evidence/Observation. `PrivacyBoundary`, `Redaction`, `ProjectionEngine`, and `Noninterference` remain candidate behaviors/constraints rather than new primitives.

## Limits
This bounded model does not prove cryptographic privacy, arbitrary non-inference, side-channel resistance, adaptive privacy, legal/organizational authorization, or real private Genesis correspondence. It also does not establish that every authorized derived dependency is safe; downstream risk and consequence require separate governance.

## Omission gate — «Ничего ли мы не упустили?»
Open: multi-field dependency graphs, transitive/derived leakage, authorization revocation during derivation, observational equivalence under adaptive queries, real private Genesis state, and canonical private CI. These remain separate boundaries.

## Decision
`BOUNDED LOCAL SUPPORT / NO NEW PRIMITIVE / NOT CANONICAL`.

## Next bounded step
Test revocation or contract change between derivation and publication: a dependency may be declared and authorized when computation starts but cease to be authorized before the public transition. The public result must then be governed by fresh authority/evidence rather than stale admission state.
