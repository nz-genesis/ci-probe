# P347 — одноразовая установка автономного Mac execution node

## Что уже подготовлено

В `nz-genesis/ci-probe` подготовлены:

- `scripts/p347_mac_jit_runner.sh` — JIT/ephemeral runner loop;
- `scripts/install_p347_mac_jit_service.sh` — пользовательский macOS LaunchAgent;
- `.github/workflows/p347-mac-node-preflight.yml` — trusted-push-only preflight;
- `probes/p347_mac_node_preflight.py` — bounded host identity probe.

Целевая ветка:

`research/p347-mac-node-preflight-v0`

## Однократное действие

На Mac:

```bash
gh auth login
git clone https://github.com/nz-genesis/ci-probe.git
cd ci-probe
git fetch origin research/p347-mac-node-preflight-v0
git checkout research/p347-mac-node-preflight-v0
bash scripts/install_p347_mac_jit_service.sh
```

После этого LaunchAgent автоматически поддерживает JIT runner.

Никакой GitHub token не нужно писать в Git, чат или файл проекта.

## Что произойдёт дальше

1. LaunchAgent запускает bounded runner bootstrap.
2. Bootstrap получает JIT configuration через GitHub API.
3. Создаётся ephemeral Mac runner с label `p347-mac`.
4. GitHub назначает ему только подходящую job.
5. Выполняется preflight.
6. Raw artifact возвращается в GitHub Actions.
7. Ephemeral runner удаляется GitHub.
8. Bootstrap готовит следующий JIT runner.

После этого ручной запуск каждой исследовательской итерации не нужен.

## Важная граница

Это **не полный P347+ execution**.

Для stronger gate всё ещё нужны:

- независимая external authority вне GitHub;
- независимый packet-level network witness;
- real partial effect;
- lost ACK;
- fresh re-observation/reconciliation;
- crash/restart/rejoin.

Mac не является witness и не может одновременно играть роль authority и witness.

## Security

Runner предназначен только для bounded P347 research.

Не помещать в runner environment:

- SSH private keys;
- production credentials;
- browser profiles;
- личные файлы;
- unrelated secrets.

Workflow специально ограничен trusted push branch и не использует `pull_request`/`pull_request_target` для Mac runner.

Официальная документация GitHub предупреждает о рисках self-hosted runners в public repositories; поэтому эта схема является экспериментальным execution substrate, а не универсальной production-рекомендацией.
