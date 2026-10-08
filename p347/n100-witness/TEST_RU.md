# P347 N100 witness — физический протокол

## На N100

    uname -a
    cat /etc/os-release
    hostname
    ip -br addr
    ip route
    command -v tcpdump
    tcpdump --version
    python3 --version
    timedatectl status
    chronyc tracking || true

Создать:

    sudo mkdir -p /var/tmp/p347-n100-witness
    sudo chmod 700 /var/tmp/p347-n100-witness

Запуск, заменив <INTERFACE> и <AUTHORITY_HOST> реальными значениями:

    sudo python3 p347/n100-witness/capture.py --interface <INTERFACE> --capture-dir /var/tmp/p347-n100-witness --target-host <AUTHORITY_HOST> --target-port 443 --duration 600

После capture:

    sudo python3 p347/n100-witness/manifest.py /var/tmp/p347-n100-witness

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

Затем, после того как известны <MAC_IP> и <AUTHORITY_IP>, выполнить:

    sudo tcpdump -i <INTERFACE> -nn -c 20 'host <MAC_IP> and host <AUTHORITY_IP> and tcp port 443'

Параллельно на Mac выполнить несколько безопасных baseline HTTPS requests к external authority и сохранить Mac-side trace.

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
4. start Mac application trace;
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
- Mac baseline application trace;
- N100 raw pcap;
- witness manifest;
- authority-side trace;
- exact source/version identity;
- synchronized wall/monotonic timing.

Если хотя бы один обязательный поток отсутствует, faulted run остаётся APPARATUS-ONLY / NOT ADMITTED.
