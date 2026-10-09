# P347 N100 witness — физический протокол

## 0. Capture harness v2 — контракт и ограничения

Harness v2 теперь:
- строит BPF filter по `--actor-ip` и одному или нескольким `--target-ip`, полученным из Mac-side application/socket trace, а не из DNS-результата N100;
- принимает только пустой run-specific capture directory;
- считает раннее завершение `tcpdump` ошибкой;
- отклоняет pcap без packet payload;
- сохраняет durable metadata с actor/target provenance и SHA-256;
- `manifest.py` проверяет обязательные файлы, hashes, start/stop event boundaries и отсутствие раннего выхода.

Контрактные тесты проверяют filter provenance, literal IP validation, fail-closed поведение каталога и manifest. Они не являются физическим packet-witness evidence. Физическое подтверждение появляется только после реального capture на N100 и корреляции с Mac-side trace.

Перед full capture сначала выполнить ручной visibility preflight из раздела 2. Не запускай fault injection, пока не получено `WITNESS_VISIBILITY = VERIFIED_BOUNDED`.

## Подготовка точного checkout на N100

Все команды ниже выполняются в терминале N100. Нужны SSH/локальный терминал, `sudo` и доступ в интернет. Для reproducibility используй проверенный capture/manifest/test code baseline:

~~~bash
set -euo pipefail
REPO_DIR="$HOME/ci-probe-p347-witness"
if [ ! -d "$REPO_DIR/.git" ]; then
  git clone https://github.com/nz-genesis/ci-probe.git "$REPO_DIR"
fi
cd "$REPO_DIR"
git fetch origin
git checkout --detach e73f3ac90f44a8cb3e3c1ca4d43d3fba345acaf1
test "$(git rev-parse HEAD)" = "e73f3ac90f44a8cb3e3c1ca4d43d3fba345acaf1"
printf 'WITNESS_SOURCE_SHA=%s\n' "$(git rev-parse HEAD)"
python3 --version
if ! command -v tcpdump >/dev/null 2>&1; then
  sudo apt-get update
  sudo apt-get install -y tcpdump
fi
tcpdump --version
~~~

Не запускай capture из неизвестного checkout и не используй старый capture directory. Если `git clone` или `git checkout` завершается ошибкой, остановись и сохрани точный текст ошибки.

## На N100

~~~bash
uname -a
cat /etc/os-release
hostname
ip -br link
ip -br addr
ip route
ip neigh
timedatectl status
chronyc tracking || true
sudo -n true && echo "SUDO_OK" || echo "SUDO_REQUIRES_PASSWORD"
~~~

После успешного visibility preflight, из корня точного checkout `ci-probe`, создай новый пустой каталог для каждой попытки:

    RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
    CAPTURE_DIR="/var/tmp/p347-n100-witness/${RUN_ID}"
    sudo mkdir -m 700 -p "$CAPTURE_DIR"

Запуск, используя `MAC_IP` и `AUTHORITY_IP`, установленные из Mac-side trace, и фактический интерфейс N100:

    sudo python3 p347/n100-witness/capture.py --interface "$INTERFACE" --capture-dir "$CAPTURE_DIR" --target-host "$AUTHORITY_HOST" --actor-ip "$MAC_IP" --target-ip "$AUTHORITY_IP" --target-port 443 --duration 600

Если Mac-side trace показывает несколько фактических remote IP, повтори `--target-ip <IP>` для каждого IP. Не подставляй DNS-ответ, полученный на N100, вместо адреса, наблюдавшегося на Mac.

После capture:

    sudo python3 p347/n100-witness/manifest.py "$CAPTURE_DIR"

Сначала сохраняется полный raw directory, только потом проводится анализ.

Mac actor отдельно должен записать request/response/timeout timestamps, correlation ID, generation, effect ID, retry и fresh observation.

Authority отдельно должен экспортировать generation transitions, effect creation, duplicate/conflict decisions и fresh observations.

Ни один из этих потоков нельзя заменять модельным выводом.


## 1. Обязательная проверка видимости witness

N100 нельзя считать независимым packet witness только потому, что tcpdump запускается успешно.

В обычной switched/Wi-Fi сети unicast-трафик между Mac и external authority может не попадать на N100 interface. Для admissible packet witness должна быть доказана topology visibility: N100 находится на реальном пути трафика либо switch/network infrastructure зеркалирует соответствующий порт/трафик на N100.

Apple прямо отмечает, что promiscuous capture на отдельной машине требует topology, позволяющей видеть packets; обычный switch не пересылает весь unicast на другие порты, поэтому для внешнего witness может потребоваться port mirroring.

### Visibility preflight — N100

На N100:

    ip -br addr
    ip route
    ip neigh
    sudo -n true && echo "SUDO_OK" || echo "SUDO_REQUIRES_PASSWORD"

Определить реальный interface:

    ip -br link

### Mac-side IP discovery — выполнить на Mac до N100 capture

Используй URL, полученный из свежего deploy по `p347/external-authority/DEPLOY_RU.md`. На Mac в терминале:

~~~bash
export P347_EXTERNAL_AUTHORITY_URL="$(cat "$HOME/.local/share/p347-authority/authority-url")"
AUTHORITY_IP="$(curl --ipv4 --http1.1 --connect-timeout 10 --max-time 20 -sS -o /dev/null -w '%{remote_ip}' "${P347_EXTERNAL_AUTHORITY_URL}/v1/state")"
MAC_IFACE="$(route -n get "$AUTHORITY_IP" | awk '/interface:/{print $2}')"
MAC_IP="$(ipconfig getifaddr "$MAC_IFACE")"
AUTHORITY_HOST="${P347_EXTERNAL_AUTHORITY_URL#https://}"
printf 'MAC_IFACE=%s\nMAC_IP=%s\nAUTHORITY_HOST=%s\nAUTHORITY_IP=%s\n' "$MAC_IFACE" "$MAC_IP" "$AUTHORITY_HOST" "$AUTHORITY_IP"
~~~

Если authority URL хранится не в этом каталоге, задай `P347_EXTERNAL_AUTHORITY_URL` вручную. Не печатай и не передавай token files. `AUTHORITY_IP` — это remote IP, наблюдавшийся на Mac, а не DNS-ответ N100.

### Visibility capture — два терминала

1. На N100 выбери интерфейс, который реально получает mirror traffic или находится на forwarding path. Нельзя автоматически выбирать default-route interface и предполагать, что он видит Mac unicast. Если switch mirroring не настроен и N100 не является forwarding path, остановись: visibility не доказана.
2. На N100 задай значения из вывода Mac и запусти capture. Этот preflight намеренно фильтрует по Mac IP и TCP/443, чтобы не пропустить другой Cloudflare edge IP; на время 30 секунд закрой браузеры и не запускай другие сетевые действия.

~~~bash
INTERFACE="<имя интерфейса из ip -br link>"
MAC_IP="<MAC_IP из Mac-side вывода>"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="$HOME/p347-n100-visibility-${RUN_ID}.txt"
set +e
set -o pipefail
sudo timeout --signal=INT 30s tcpdump -i "$INTERFACE" -nn -s 0 -tttt "host $MAC_IP and tcp port 443" 2>&1 | tee "$OUT"
CAPTURE_EXIT=$?
set +o pipefail
printf 'VISIBILITY_CAPTURE_EXIT=%s\nOUTPUT=%s\n' "$CAPTURE_EXIT" "$OUT"
~~~

3. Пока команда выше работает, на Mac запусти три read-only requests в том же терминале:

~~~bash
for i in 1 2 3; do
  curl --ipv4 --http1.1 --connect-timeout 10 --max-time 20 -sS -o /dev/null \
    -w "request=$i remote_ip=%{remote_ip} remote_port=%{remote_port} http_code=%{http_code}\n" \
    "${P347_EXTERNAL_AUTHORITY_URL}/v1/state"
done
~~~

Сравни каждый `remote_ip` с destination IP в N100 tcpdump output. Если IP меняется между запросами, сохрани все IP и используй их в full capture как повторяющиеся `--target-ip` параметры. `VISIBILITY_CAPTURE_EXIT=124` означает, что окно завершилось по timeout; само по себе это не ошибка и не доказательство потери. Важно, чтобы output содержал packets известного Mac → authority flow, а Mac-side trace подтверждал эти же запросы. Нулевой capture означает `WITNESS_VISIBILITY = UNVERIFIED`, не packet loss.

### Admission rule

- Если N100 видит ожидаемые packets и application trace на Mac подтверждает тот же flow → WITNESS_VISIBILITY = VERIFIED_BOUNDED.
- Если N100 capture пуст, но Mac trace подтверждает traffic → это НЕ packet-loss evidence; topology visibility не доказана.
- Если N100 видит только DNS/ARP/локальный traffic, но не target flow → это также НЕ witness evidence.
- Если interface не поддерживает необходимую capture mode или topology не предоставляет traffic visibility → остановить физический эксперимент до исправления topology.
- Нельзя превращать отсутствие packet в LOSS, пока одновременно не выполнены capture-completeness, topology-visibility и application-correlation gates.

### Рекомендуемая topology

Предпочтительно:

    Mac actor ── switch port A
                    │
                    ├── mirrored traffic ── N100 witness
                    │
                    └── uplink ── router/Internet ── external authority

Альтернатива:

    Mac actor ── N100 forwarding/bridge ── router/Internet ── external authority

Но в альтернативе N100 уже участвует в forwarding path; поэтому для stronger independence предпочтителен passive mirrored port, если сеть это позволяет.

Wi-Fi-only topology без доказанной monitor-mode/traffic-visibility capability не принимается как independent packet witness.

## 2. Fault injection boundary

N100 не должен одновременно быть fault injector и witness.

Для lost-ACK variation fault должен управляться на actor-side или отдельной network-control boundary, тогда как N100 остаётся пассивным witness.

Mac-side PF может использоваться как experimental fault mechanism только после отдельного preflight и с обратимым named anchor. Apple отмечает, что PF существует в macOS, но не является стабильным public API; поэтому его использование здесь является bounded test apparatus, а не production architecture.

Минимальная последовательность:

1. baseline без fault;
2. verify N100 visibility;
3. start N100 raw capture;
4. start the tested Mac actor/application trace and record the actual remote IP;
5. establish correlation ID;
6. initiate one consequential effect;
7. activate a narrowly scoped, reversible response-drop window;
8. preserve Mac timeout/unknown result;
9. verify from authority that the effect may have committed;
10. remove fault;
11. perform fresh observation;
12. perform idempotent retry with the same key;
13. compare authority effect identity and N100 packet trace;
14. preserve raw artifacts before analysis.

Не блокировать весь Mac traffic. Fault rule должна быть ограничена target authority/IP/port и только необходимым direction/window.

## 3. Physical evidence gate

До первой faulted run должны существовать одновременно:

- N100 topology-visibility evidence;
- dedicated Mac actor script, tested against the real external authority and emitting the correlated application trace;
- Mac baseline application trace with actual local/remote IPs;
- N100 raw pcap;
- witness manifest;
- authority-side trace;
- exact source/version identity;
- synchronized wall/monotonic timing.

**Текущий статус Mac actor (2026-10-09):** dedicated actor реализован в p347/mac-actor/actor.py. Текущий branch HEAD — `6b7675ec70159187a68d4792ac0be9c1a8f724e2`; run `37912388643` является историческим receipt для предыдущего actor source `0eb631c597f2b3705a8f211245f123767b994c14`. Hosted-Linux contract tests 11/11 PASS, Node contract tests 17/17 PASS, external authority 7/7 PASS в этом историческом receipt. После появления нового HEAD старый receipt не является подтверждением нового source; перед физическим запуском нужен новый exact-source workflow receipt. Это закрывает только artifact/contract gap. Физический Mac runtime и N100 visibility всё ещё PENDING; lost_ack_exercised остаётся false до независимого fault-controller receipt и коррелированного N100 raw pcap/manifest.

Workflow-assisted read-only preflight находится в .github/workflows/p347-mac-visibility-preflight.yml и запускается на self-hosted Mac runner. В логах появляется N100_CAPTURE_WINDOW_OPEN с MAC_IP, AUTHORITY_IP и задержкой 120 секунд до трёх read-only GET probes. Во время окна на N100 нужно запустить capture длительностью не менее 240 секунд, фильтр host MAC_IP и TCP/443. Сопоставь capture с Mac-side request timestamps и фактическими remote IP из артефакта. Если окно пропущено, visibility остаётся PENDING и preflight нужно повторить при готовом N100 capture.

Read-only discovery не запускает mutation/effect и не активирует fault injector. Он не доказывает видимость N100 сам по себе и не разрешает faulted physical run.

Если хотя бы один обязательный поток отсутствует, faulted run остаётся APPARATUS-ONLY / NOT ADMITTED.
