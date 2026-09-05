"""P306 empirical total-cost benchmark for sufficient control.

This is a new workload family, not a replay of earlier selector/workload probes.
It compares GOVERNED (all tasks) with ADAPTIVE (only consequential/high-risk tasks)
and keeps DIRECT only as a negative safety control.

The benchmark randomizes policy order across repeated trials, measures local wall time,
verification count and a transparent cost proxy, and computes the verification-cost
threshold at which ADAPTIVE becomes cheaper than GOVERNED. The proxy is not a universal
economic metric and no claim of universal adaptive superiority is made.

The purpose is to test the TRIZ direction "sufficient control rather than maximum
control" while preserving the protected boundary.
"""
from random import Random
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
    task_checksum = 0
    control_checksum = 0
    for _ in range(rounds):
        for name, units, consequential, risk in WORKLOADS:
            governed = policy == "GOVERNED" or (policy == "ADAPTIVE" and consequential)
            if consequential and not governed:
                unsafe += 1
            if governed:
                verifications += 1
                control_checksum = (control_checksum + work(20 + risk * 3)) & 0xFFFFFFFF
            task_checksum = (task_checksum + work(units)) & 0xFFFFFFFF
            operations += 1
    elapsed = perf_counter() - start
    return elapsed, operations, verifications, unsafe, task_checksum, control_checksum


def benchmark(trials=15):
    rng = Random(306)
    samples = {p: [] for p in ("DIRECT", "GOVERNED", "ADAPTIVE")}
    for _ in range(trials):
        policies = ["DIRECT", "GOVERNED", "ADAPTIVE"]
        rng.shuffle(policies)
        for policy in policies:
            samples[policy].append(run(policy))
    return {
        p: (
            median(x[0] for x in samples[p]),
            samples[p][0][1],
            samples[p][0][2],
            samples[p][0][3],
            samples[p][0][4],
            samples[p][0][5],
        )
        for p in samples
    }


def main():
    results = benchmark()
    direct = results["DIRECT"]
    governed = results["GOVERNED"]
    adaptive = results["ADAPTIVE"]

    # DIRECT is intentionally a negative control: consequential work is ungoverned.
    assert direct[3] > 0
    # Both viable policies protect every consequential task.
    assert governed[3] == 0
    assert adaptive[3] == 0
    # Adaptive performs fewer verification operations on this workload.
    assert adaptive[2] < governed[2]
    # All policies execute the same task workload and produce the same task result.
    assert direct[1] == governed[1] == adaptive[1]
    assert direct[4] == governed[4] == adaptive[4]

    verification_delta = governed[2] - adaptive[2]
    wall_delta = adaptive[0] - governed[0]
    threshold_us = (wall_delta / verification_delta) * 1e6

    print("P306 local sufficient-control benchmark: PASS")
    for label, result in results.items():
        elapsed, operations, verifications, unsafe, task_checksum, control_checksum = result
        print(
            f"{label}: median_wall={elapsed:.6f}s operations={operations} "
            f"verifications={verifications} unsafe_consequential={unsafe} "
            f"task_checksum={task_checksum} control_checksum={control_checksum}"
        )
    print(
        f"ADAPTIVE_vs_GOVERNED: verification_reduction={verification_delta}; "
        f"wall_delta={wall_delta:.6f}s; "
        f"break_even_verification_cost={threshold_us:.3f}us"
    )


if __name__ == "__main__":
    main()
