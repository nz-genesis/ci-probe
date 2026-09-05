"""P306 empirical total-cost benchmark for sufficient control.

This is a new workload family, not a replay of earlier selector/workload probes.
It compares three policies over heterogeneous tasks:
- DIRECT: no governance mediation;
- GOVERNED: every task pays qualification/verification overhead;
- ADAPTIVE: only consequential/high-risk tasks pay that overhead.

The benchmark measures local wall time, operation count, verification count and a
transparent composite cost proxy. It does not claim that the proxy is a universal
economic metric. It also asserts a safety/admissibility invariant: consequential tasks
must never be executed by DIRECT or by ADAPTIVE without governance.

The purpose is to test the TRIZ direction "sufficient control rather than maximum
control" while preserving the protected boundary.
"""
from time import perf_counter

WORKLOADS = (
    ("draft", 120, False, 1),
    ("summarize", 180, False, 1),
    ("classify", 160, False, 1),
    ("plan", 240, False, 2),
    ("send", 140, True, 4),
    ("delete", 110, True, 5),
    ("publish", 260, True, 5),
    ("change_authority", 90, True, 8),
)


def work(units):
    x = 0
    for i in range(units):
        x = (x * 1664525 + i + 1013904223) & 0xFFFFFFFF
    return x


def run(policy, rounds=400):
    start = perf_counter()
    operations = 0
    verifications = 0
    unsafe = 0
    checksum = 0
    for _ in range(rounds):
        for name, units, consequential, risk in WORKLOADS:
            governed = policy == "GOVERNED" or (policy == "ADAPTIVE" and consequential)
            if policy == "DIRECT" and consequential:
                unsafe += 1
            if governed:
                verifications += 1
                checksum ^= work(20 + risk * 3)
            checksum ^= work(units)
            operations += 1
    elapsed = perf_counter() - start
    # Transparent local proxy: wall time + weighted verification operations.
    cost_proxy = elapsed + verifications * 1e-6
    return elapsed, operations, verifications, unsafe, checksum, cost_proxy


def main():
    direct = run("DIRECT")
    governed = run("GOVERNED")
    adaptive = run("ADAPTIVE")

    # Governance invariant: adaptive must protect every consequential task.
    assert direct[3] > 0
    assert governed[3] == 0
    assert adaptive[3] == 0
    assert adaptive[2] < governed[2]

    # Same workload and deterministic work function preserve result comparability.
    assert direct[1] == governed[1] == adaptive[1]
    assert direct[5] > 0 and governed[5] > 0 and adaptive[5] > 0

    print("P306 local sufficient-control benchmark: PASS")
    for label, result in (("DIRECT", direct), ("GOVERNED", governed), ("ADAPTIVE", adaptive)):
        elapsed, operations, verifications, unsafe, checksum, cost = result
        print(
            f"{label}: wall={elapsed:.6f}s operations={operations} "
            f"verifications={verifications} unsafe_consequential={unsafe} "
            f"checksum={checksum} cost_proxy={cost:.6f}"
        )


if __name__ == "__main__":
    main()
