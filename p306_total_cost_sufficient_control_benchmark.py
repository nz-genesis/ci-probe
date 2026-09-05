"""P306 empirical total-cost benchmark for sufficient control.

This is a new workload family, not a replay of earlier selector/workload probes.
It compares GOVERNED (all tasks) with ADAPTIVE (only consequential/high-risk tasks)
and keeps DIRECT only as a negative safety control.

The benchmark measures repeated local wall time, operation count, verification count
and a transparent local cost proxy. It does not claim that the proxy is a universal
economic metric. It asserts the safety/admissibility invariant that every consequential
operation is governed by ADAPTIVE and GOVERNED.

The purpose is to test the TRIZ direction "sufficient control rather than maximum
control" while preserving the protected boundary.
"""
from statistics import median
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
    x = 2166136261
    for i in range(units):
        x ^= i + 101
        x = (x * 16777619) & 0xFFFFFFFF
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
            if consequential and not governed:
                unsafe += 1
            if governed:
                verifications += 1
                checksum = (checksum + work(20 + risk * 3)) & 0xFFFFFFFF
            checksum = (checksum + work(units)) & 0xFFFFFFFF
            operations += 1
    elapsed = perf_counter() - start
    # Transparent local proxy: measured wall time + one microsecond per verification.
    cost_proxy = elapsed + verifications * 1e-6
    return elapsed, operations, verifications, unsafe, checksum, cost_proxy


def benchmark(policy, trials=7):
    samples = [run(policy) for _ in range(trials)]
    return (
        median(x[0] for x in samples),
        samples[0][1],
        samples[0][2],
        samples[0][3],
        samples[0][4],
        median(x[5] for x in samples),
    )


def main():
    direct = benchmark("DIRECT")
    governed = benchmark("GOVERNED")
    adaptive = benchmark("ADAPTIVE")

    # DIRECT is intentionally a negative control: consequential work is ungoverned.
    assert direct[3] > 0
    # Both viable policies protect every consequential task.
    assert governed[3] == 0
    assert adaptive[3] == 0
    # Adaptive control is strictly smaller on this workload family.
    assert adaptive[2] < governed[2]
    # Comparability and deterministic workload result are preserved.
    assert direct[1] == governed[1] == adaptive[1]
    assert len({direct[4], governed[4], adaptive[4]}) == 3

    print("P306 local sufficient-control benchmark: PASS")
    for label, result in (("DIRECT", direct), ("GOVERNED", governed), ("ADAPTIVE", adaptive)):
        elapsed, operations, verifications, unsafe, checksum, cost = result
        print(
            f"{label}: median_wall={elapsed:.6f}s operations={operations} "
            f"verifications={verifications} unsafe_consequential={unsafe} "
            f"checksum={checksum} median_cost_proxy={cost:.6f}"
        )


if __name__ == "__main__":
    main()
