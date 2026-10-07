#!/usr/bin/env python3
"""Hosted executable verification for the Genesis₀ test apparatus.

The probe deliberately does not copy Genesis code into ci-probe. It fetches the
exact Genesis Lab commit under test and executes the repository's own test
commands. This keeps GitHub source-of-truth and evidence provenance separate.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "https://github.com/nz-genesis/genesis-lab.git"
COMMIT = os.environ.get("GENESIS_LAB_COMMIT", "1c49b9e654ddcce001556740a76a5a8ba9f4ad7a")
TESTS = [  # Exact Genesis₀ + V0 Gate-1 test set: 48 tests.

    "genesis/experimental/semantic_kernel_v0/test_kernel.py",
    "genesis/experimental/semantic_kernel_v0/test_cognitive_boundary.py",
    "genesis/experimental/semantic_kernel_v0/test_effect_protocol.py",
    "genesis/genesis0/test_core.py",
]


def run(*args: str, cwd: Path | None = None) -> None:
    print("$", " ".join(args), flush=True)
    subprocess.run(args, cwd=cwd, check=True)


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="genesis0-ci-") as tmp:
        worktree = Path(tmp) / "genesis-lab"
        run("git", "clone", "--no-tags", "--depth", "1", REPO, str(worktree))
        run("git", "fetch", "--no-tags", "origin", COMMIT, cwd=worktree)
        run("git", "checkout", "--detach", COMMIT, cwd=worktree)

        print(f"GENESIS_LAB_COMMIT={COMMIT}", flush=True)
        run(
            sys.executable,
            "-m",
            "pytest",
            *TESTS,
            "-q",
            cwd=worktree,
        )
        print(f"GENESIS0_CI_PROBE=PASS commit={COMMIT} tests=48", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
