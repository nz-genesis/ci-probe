# P347 N100 Network Witness V1

Независимый физический witness для наблюдения Mac actor ↔ external authority.

Не эмулирует сеть, authority или ACK и не создаёт semantic evidence сам по себе.

Admissible raw evidence:
- pcap;
- monotonic + UTC timestamps;
- witness host identity;
- capture interface;
- observed DNS/IP target;
- correlation ID;
- raw application traces;
- SHA-256 manifest.

Запрещено выводить packet loss только из отсутствия записи без проверки полноты capture.

Статус: APPARATUS-DEFINED / PHYSICAL-EXECUTION-PENDING
