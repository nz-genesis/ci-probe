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
