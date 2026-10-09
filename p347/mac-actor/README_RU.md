# P347 Mac actor — клиент внешней authority

## Назначение и границы

actor.py выполняет внешний P347 сценарий с точным actor checkout, фактическими local/remote IP из curl, HTTP status, UTC и monotonic timestamps, correlation ID, idempotency key/fingerprint и reconciliation.

Actor не активирует и не управляет fault injector. N100 остаётся пассивным witness. Evidence никогда само по себе не объявляет физический эффект или независимость witness допущенными.

## Перед запуском

- Сначала выполни read-only Mac↔N100 visibility preflight из p347/n100-witness/TEST_RU.md.
- Разверни свежую external authority из того же exact source SHA, который используется для actor checkout. Для workflow-assisted preflight это `$GITHUB_SHA`; для manual run используй `ACTOR_SHA` из exact clean checkout и передай тот же SHA как `--expected-source-version`. Не pin-ь authority на исторический SHA из предыдущего run.
- Секреты храни только вне Git: ~/.local/share/p347-authority/{authority-url,admin-token,effect-token}. Token files должны иметь mode 0600; URL-файл содержит только workers.dev URL, не claim URL.
- Не печатай tokens, не включай их в evidence и не загружай секреты в публичные артефакты. Actor передаёт Authorization через временный файл mode 0600, не через argv; файл удаляется после единственного curl-вызова. Read-only GET повторяется ограниченно только при UNKNOWN/HTTP 523/Cloudflare 1042/1104; mutation не повторяется, consequential POST отправляется ровно один раз.
- Используй clean exact actor checkout; prepare остановится на dirty tree.

## Workflow-assisted topology preflight

Workflow: .github/workflows/p347-mac-visibility-preflight.yml.

- A push to this branch performs only a hosted-Linux deployment/readiness diagnostic. It must not run physical Mac probes.
- The physical Mac job runs only when a push to research/p347-mac-actor-v0 has the exact commit-message marker [P347-PHYSICAL-ARMED], or via workflow_dispatch after the workflow is available on the default branch. Never put the marker on ordinary code/documentation commits. Do not arm the physical job until N100 is open and the operator is ready to begin capture as soon as the initial Mac probe emits N100_CAPTURE_WINDOW_OPEN. The GitHub connector used in this pass cannot dispatch workflows, and this PR is still draft, so no physical run is being armed here.
- Before the Mac job is allowed to run, the hosted-Linux readiness probe must observe HTTP 200 JSON with authority=P347_EXTERNAL_AUTHORITY and source_version equal to the exact triggering SHA. It retries only bounded known transient transport/1042/1104/523 conditions. HTTP 401/403 challenges and source mismatches fail closed.
- After readiness passes, the physical Mac runner deploys/probes the same exact source and emits actual MAC_IP/AUTHORITY_IP plus a 120-second capture window before three read-only GET probes. During that window, N100 must capture host MAC_IP and TCP/443 for at least 240 seconds using the actual remote IP reported by Mac. Preserve raw pcap and manifest.
- The workflow never starts or configures the fault injector. If the window is missed or no target-flow packets are observed, WITNESS_VISIBILITY remains PENDING/UNVERIFIED. A failed readiness diagnostic is not packet-loss evidence and must not be bypassed by running the Mac job directly.
- Current official Cloudflare temporary-account guidance describes --temporary as a preview/test path and recommends a permanent account for production CI/CD: https://developers.cloudflare.com/workers/platform/claim-deployments/. A 403 challenge is a run-specific observation, not permission to bypass Cloudflare controls.

## 1. Точный checkout и тесты на Mac

Задай ACTOR_SHA точным SHA проверенного commit/workflow, а не именем плавающей ветки:

~~~
set -euo pipefail
ACTOR_SHA="<точный commit SHA из GitHub>"
REPO_DIR="$HOME/ci-probe-p347-actor"
if [ ! -d "$REPO_DIR/.git" ]; then git clone https://github.com/nz-genesis/ci-probe.git "$REPO_DIR"; fi
git -C "$REPO_DIR" fetch origin
git -C "$REPO_DIR" checkout --detach "$ACTOR_SHA"
test "$(git -C "$REPO_DIR" rev-parse HEAD)" = "$ACTOR_SHA"
EXPECTED_AUTHORITY_SHA="$ACTOR_SHA"
test "$EXPECTED_AUTHORITY_SHA" = "$ACTOR_SHA"
# Authority source and actor source MUST be identical for this run.
printf 'ACTOR_SHA=%s\nEXPECTED_AUTHORITY_SHA=%s\n' "$ACTOR_SHA" "$EXPECTED_AUTHORITY_SHA"
test -z "$(git -C "$REPO_DIR" status --porcelain --untracked-files=normal)"
cd "$REPO_DIR"
python3 --version
curl --version
python3 -m unittest discover -s p347/mac-actor -p 'test_*.py' -v
~~~

При любой ошибке остановись и сохрани точный вывод.

## 2. Подготовить свежую authority

~~~
set -euo pipefail
SECRET_DIR="$HOME/.local/share/p347-authority"
test -f "$SECRET_DIR/authority-url"
test -f "$SECRET_DIR/admin-token"
test -f "$SECRET_DIR/effect-token"
test "$(stat -f '%Lp' "$SECRET_DIR/admin-token")" = "600"
test "$(stat -f '%Lp' "$SECRET_DIR/effect-token")" = "600"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
RUN_DIR="$HOME/p347-mac-actor-runs/$RUN_ID"
python3 p347/mac-actor/actor.py prepare --expected-source-version "$EXPECTED_AUTHORITY_SHA" --run-dir "$RUN_DIR"
~~~

prepare требует generation 1, effect_count 0 и точный source_version. Выполняет одно изменение generation и проверяет stale-generation rejection. Если ответ mutation неоднозначен, делает только fresh read-only observation; mutation автоматически не повторяет.

## 3. Один consequential request

Выполняй только после запуска N100 capture и проверки, что внешний fault controller отдельно подготовлен:

~~~
python3 p347/mac-actor/actor.py effect-once --run-dir "$RUN_DIR" --timeout-seconds 3
~~~

Команда делает ровно один POST /v1/effects. Если HTTP response не наблюдался, результат UNKNOWN — это не означает, что эффект не произошёл. Без отдельно подтверждённого response-drop fault результат не является lost-ACK evidence.

## 4. Reconciliation после снятия fault

После того как отдельный controller подтвердил снятие правила:

~~~
python3 p347/mac-actor/actor.py reconcile --run-dir "$RUN_DIR"
~~~

Actor выполняет fresh observation, один same-key/same-payload retry, same-key/different-payload conflict и финальное наблюдение. Если fresh observation UNKNOWN, actor останавливается до retry.

ambiguous_effect_recovery=VERIFIED_BOUNDED возможно только если первоначальный запрос был UNKNOWN, fresh observation до retry уже увидел эффект, retry вернул тот же effect как duplicate, конфликт отклонён, а финальное наблюдение подтвердило исходный эффект. Это доказывает восстановление после неоднозначного ответа на уровне actor, но не доказывает намеренную потерю ACK. lost_ack_exercised остаётся false до независимого fault-controller receipt и коррелированного N100 raw pcap/manifest.

## 5. Evidence

Каталог RUN_DIR остаётся локальным и приватным. Не загружай его автоматически в публичный CI. Сопоставь evidence с authority trace, Mac-side socket/application trace, N100 raw pcap/events/meta/manifest и точными source identities.

P347_MAC_ACTOR_* означает только результат actor stage. Это не закрывает WITNESS_VISIBILITY, lost-ACK/partition, physical effect или P347+ gate.
