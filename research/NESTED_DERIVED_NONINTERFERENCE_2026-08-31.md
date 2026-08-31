# P196 — Nested Derived-Field Noninterference — 2026-08-31

**Status:** `EXPERIMENTAL / EXECUTABLE / LOCAL PASS / HOSTED-CI PENDING / NOT CANONICAL`

## Global Purpose
Глобальная цель Genesis остаётся неизменной; этот bounded pass не изменяет Purpose, identity или canonical ontology.

## Current goal
Проверить более сильную границу private→public correspondence: nested private mutations и adversarial derived public fields не должны создавать ложную public semantic change или раскрывать private state; public semantic mutations должны оставаться наблюдаемыми.

## Non-duplication
P190 уже проверяет минимальную private→public correspondence, а существующий derived-field probe проверяет простые private fields. P196 добавляет materially different nested state и, главное, adversarial derived projection, который намеренно пытается внедрить private score в public derived value. Verifier должен обнаружить плохую projection, а не просто подтвердить форму хорошей реализации.

## Executable evidence
`nz-genesis/ci-probe/nested_derived_noninterference.py`

Workflow:
`.github/workflows/nested-derived-noninterference.yml`

## Local execution
Exact committed probe logic was independently reproduced in a clean Python environment and produced:

`NESTED DERIVED NONINTERFERENCE: 8/8 PASS`

Hosted CI is not claimed until a completed run for the exact commit is independently inspected.

## Red Team
The probe covers nested private-note mutation, nested private-score mutation, observable public mutation, direct private-output absence, and an adversarial derived projection that leaks private score. The adversarial projection is required to fail the noninterference check.

## Primitive reduction
No new Genesis primitive is justified. Noninterference remains a constraint/behavior over State, Authority, Evidence and Projection/representation rather than a `PrivacyBoundary`, `Redaction`, `ProjectionEngine`, or `Noninterference` primitive.

## Limits
This bounded model does not prove cryptographic privacy, arbitrary non-inference, timing/side-channel resistance, adaptive attacks, authorization completeness, or correspondence with real private Genesis state. It also does not establish global semantic minimality.

## Decision
Bounded nested noninterference is locally supported. The result remains experimental and non-canonical pending hosted verification and the broader private→public correspondence gate.

## Next discriminator
Use authorization-dependent public derivation and observational equivalence across multiple nested private states, including cases where a private mutation is legitimately allowed to influence a public derived value only when the semantic contract declares that dependency public. The verifier must distinguish declared semantic dependency from accidental leakage.
