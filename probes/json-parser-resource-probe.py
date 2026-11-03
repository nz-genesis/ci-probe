#!/usr/bin/env python3
"""Generic CPython JSON parser materialization probe.

This probe measures standard-library JSON decoding in isolated child processes.
It contains no private project code, configuration, fixtures, or semantics.
Results are observations for the exact runner/runtime only; no universal memory
threshold is asserted.
"""
from __future__ import annotations

import json
import os
import platform
import resource
import subprocess
import sys
import time
from typing import Any

MIB = 1024 * 1024
TARGET_SIZES = (1 * MIB, 4 * MIB, 8 * MIB)


def current_rss_kib() -> int:
    """Read current Linux resident-set size in KiB."""
    with open("/proc/self/status", "r", encoding="ascii") as stream:
        for line in stream:
            if line.startswith("VmRSS:"):
                return int(line.split()[1])
    raise RuntimeError("VmRSS is unavailable on this Linux runner")


def reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    """Generic duplicate-key hook matching a common strict-decoder pattern."""
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def worker(case: str) -> int:
    raw = sys.stdin.read()
    input_bytes = len(raw.encode("utf-8"))
    if input_bytes > max(TARGET_SIZES):
        raise ValueError("worker input exceeds the probe's maximum size")
    baseline_rss_kib = current_rss_kib()
    started = time.perf_counter()

    if case == "array":
        parsed = json.loads(raw)
    elif case == "object_pairs_hook":
        parsed = json.loads(raw, object_pairs_hook=reject_duplicate_pairs)
    else:
        raise ValueError(f"unknown worker case: {case}")

    elapsed_seconds = time.perf_counter() - started
    peak_rss_kib = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if not isinstance(parsed, (list, dict)):
        raise AssertionError("unexpected top-level JSON type")

    print(
        json.dumps(
            {
                "case": case,
                "input_bytes": input_bytes,
                "top_level_items": len(parsed),
                "parse_seconds": round(elapsed_seconds, 6),
                "baseline_rss_kib": baseline_rss_kib,
                "peak_rss_kib": peak_rss_kib,
                "incremental_peak_rss_kib": max(0, peak_rss_kib - baseline_rss_kib),
            },
            sort_keys=True,
        )
    )
    return 0


def make_array_payload(target_bytes: int) -> str:
    # Dense scalar arrays maximize item count for a given JSON byte size.
    count = max(1, (target_bytes - 1) // 2)
    payload = "[" + ("0," * (count - 1)) + "0]"
    return payload.ljust(target_bytes)


def make_object_payload(target_bytes: int) -> str:
    # Unique short keys exercise object-pair accumulation and a strict hook.
    count = max(1, (target_bytes - 1) // 14)
    members = (f'"k{index:08x}":0' for index in range(count))
    payload = "{" + ",".join(members) + "}"
    return payload.ljust(target_bytes)


def run_case(case: str, target_bytes: int) -> dict[str, Any]:
    payload = (
        make_array_payload(target_bytes)
        if case == "array"
        else make_object_payload(target_bytes)
    )
    actual_bytes = len(payload.encode("utf-8"))
    if actual_bytes != target_bytes:
        raise AssertionError("generated payload does not match its exact target size")

    completed = subprocess.run(
        [sys.executable, __file__, "--worker", case],
        input=payload,
        text=True,
        encoding="utf-8",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"worker failed for {case}/{target_bytes}: "
            f"exit={completed.returncode}; stderr={completed.stderr}"
        )
    result = json.loads(completed.stdout)
    if result["input_bytes"] != actual_bytes:
        raise AssertionError("worker input byte count does not match generated payload")
    result["target_bytes"] = target_bytes
    result["size_mib"] = round(actual_bytes / MIB, 3)
    return result


def main() -> int:
    if len(sys.argv) == 3 and sys.argv[1] == "--worker":
        return worker(sys.argv[2])

    results = [
        run_case(case, target)
        for target in TARGET_SIZES
        for case in ("array", "object_pairs_hook")
    ]
    report = {
        "probe": "generic-cpython-json-parser-materialization",
        "python_version": platform.python_version(),
        "implementation": platform.python_implementation(),
        "platform": platform.platform(),
        "runner_os": os.environ.get("RUNNER_OS", "local-linux"),
        "github_sha": os.environ.get("GITHUB_SHA"),
        "results": results,
        "interpretation": (
            "Measurements describe this exact runtime and runner only. "
            "They do not establish a universal threshold or any private "
            "application's complete resource envelope."
        ),
    }
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
