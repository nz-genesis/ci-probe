#!/usr/bin/env python3
"""Generic hosted-CI boundary control probe.

This file is deliberately Genesis-agnostic and contains no private source,
research corpus, credentials, prompts, or private identifiers.

It checks only the execution apparatus needed by a class of private workflows:
- exact checkout identity;
- Python 3.12 runtime;
- deterministic unittest discovery/execution;
- no network/private dependency.
"""

from __future__ import annotations

import hashlib
import os
import platform
import subprocess
import sys
import tempfile
import textwrap
from pathlib import Path


def run(*args: str) -> str:
    p = subprocess.run(args, check=True, text=True, capture_output=True)
    return p.stdout.strip()


def main() -> int:
    sha = os.environ.get("GITHUB_SHA", "")
    head = run("git", "rev-parse", "HEAD")
    if not sha or head != sha:
        raise SystemExit(f"CHECKOUT_IDENTITY_FAIL github_sha={sha!r} head={head!r}")

    if sys.version_info[:2] != (3, 12):
        raise SystemExit(f"PYTHON_VERSION_FAIL version={sys.version}")

    with tempfile.TemporaryDirectory(prefix="ci-boundary-") as td:
        root = Path(td)
        (root / "test_fixture.py").write_text(
            textwrap.dedent(
                """
                import hashlib
                import unittest

                class BoundaryFixture(unittest.TestCase):
                    def test_deterministic_hash(self):
                        self.assertEqual(
                            hashlib.sha256(b"ci-probe-boundary-fixture").hexdigest(),
                            "0949f47005684d28ca00720aff31a20396a5678608de8a2b125cc209ffeee9df",
                        )

                    def test_runtime(self):
                        self.assertEqual(__import__("sys").version_info[:2], (3, 12))

                if __name__ == "__main__":
                    unittest.main()
                """
            ).strip()
            + "\n",
            encoding="utf-8",
        )
        # Discoverability/execution is tested with an explicit suite so the
        # public control remains independent of repository-specific source.
        result = subprocess.run(
            [sys.executable, "-m", "unittest", "discover", "-s", str(root), "-p", "test_*.py"],
            check=False,
            text=True,
            capture_output=True,
        )
        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr, file=sys.stderr)
            raise SystemExit("UNITTEST_DISCOVERY_EXECUTION_FAIL")

    print("PRIVATE_CI_BOUNDARY_CONTROL: PASS")
    print(f"python={sys.version.split()[0]}")
    print(f"platform={platform.platform()}")
    print(f"head_sha={head}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
