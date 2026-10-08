# P347 — Mac как дополнительный execution source

**Статус:** ACTIVE / BOUNDED EXECUTION-SOURCE EXTENSION
**Дата:** 2026-10-08

## Решение

Подключённый физический Mac считается новым **execution source** Genesis research: отдельная физическая машина, отдельная ОС и сетевой стек, отдельная runtime environment и реальный self-hosted/JIT execution path.

Mac **не считается автоматически независимым semantic source** и не получает статус material external independence для IR-V3 только потому, что он физически отделён от основной рабочей машины.

## Доказательные классы

| Класс | Mac |
|---|---|
| Реальная execution environment | YES |
| Differential realization | YES |
| OS/network boundary | YES |
| Physical/network experiment | потенциально YES, после отдельного bounded test |
| Independent semantic reconstruction | NO, пока оператор контролирует Mac |
| Independent authority | NO |
| Independent witness | NO, если Mac участвует как actor |
| IR-V3 clean external participant | NO |

## Правильные вариации проверок

### V1 — Mac execution identity

Реальная машина, точный checkout и runtime capabilities проверяются через `probes/p347_mac_execution_matrix.py`.

### V2 — Differential realization

Один и тот же bounded contract выполняется на hosted Linux, физическом Mac и далее, при наличии безопасного контура, N100. Сравниваются contract digest, exact source revision, runtime identity, observable result и error class. Timing/ordering сравниваются только если они входят в claim.

Различия среды не должны превращаться в новые Genesis primitives без semantic discriminator.

### V3 — Mac ↔ N100 network boundary

Следующий material runtime pass:

Mac actor → external authority → N100 independent witness → controlled packet loss/delay → partial effect / lost ACK → fresh observation → reconciliation → idempotent retry.

Mac является actor/execution source; N100 должен быть отдельным observer/witness. Нельзя совмещать actor, authority и witness.

### V4 — IR-V3 semantic independence

Текущий owner-controlled Mac для этого не подходит. IR-V3 independence возможна только при materially independent control и blind provenance boundary.

## TRIZ

Противоречие: нужен физически отдельный runtime, но физическое разделение не даёт semantic independence.

Разделение ролей: Mac = execution evidence; внешний participant = semantic independence; external authority = authority independence; N100/network witness = observation independence.

## Gate

V1 — physical execution pending; V2 — available after same-contract run; V3 — pending; V4 — not claimed.

Это расширяет evidence surface, но не закрывает R4.1 и не меняет candidate basis.

## Security

Mac workflow: trusted branch, no pull-request execution, JIT/ephemeral runner, exact commit checkout, artifact capture, no production credentials, no browser profiles, no unrelated secrets.

## Downstream

Фиксировать в Genesis MOC/owning artifact: `MAC_EXECUTION_SOURCE = AVAILABLE`, но не `INDEPENDENT_SEMANTIC_SOURCE = AVAILABLE`. Следующий material discriminator — V3 Mac↔N100 network witness experiment.
