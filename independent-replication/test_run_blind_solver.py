#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "independent-replication" / "run_blind_solver.py"
COMMIT_VERIFY = ROOT / "tools" / "verify_commitment.py"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def expect(condition, message):
    if not condition:
        raise AssertionError(message)


def main() -> None:
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        challenge = tmp / "challenge.json"
        challenge_bytes = b'{"challenge_id":"TEST","cases":[{"id":"C1","requirement":"x"}]}\n'
        challenge.write_bytes(challenge_bytes)

        solver = tmp / "solver.py"
        solver.write_text(
            "import sys\n"
            "data=sys.stdin.buffer.read()\n"
            "assert b'FROZEN CHALLENGE BYTES BEGIN' in data\n"
            "assert b'Genesis private' not in data\n"
            "sys.stdout.buffer.write(b'blind-result-v1\\n')\n",
            encoding="utf-8",
        )

        out = tmp / "bundle"
        result = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--challenge",
                str(challenge),
                "--output-dir",
                str(out),
                "--participant-id",
                "test-solver",
                "--participant-type",
                "separate-process-control",
                "--",
                sys.executable,
                str(solver),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        expect(result.returncode == 0, f"runner failed: {result.stderr}")
        expect((out / "raw_result.bin").read_bytes() == b"blind-result-v1\n", "raw output changed")

        provenance = json.loads((out / "provenance.json").read_text(encoding="utf-8"))
        expect(provenance["challenge_sha256"] == sha256(challenge_bytes), "challenge digest mismatch")
        expect(provenance["raw_result_sha256"] == sha256(b"blind-result-v1\n"), "raw digest mismatch")
        expect(provenance["epistemic_status"] == "RAW_BLIND_RUN; NOT_EXTERNAL_INDEPENDENCE_BY_ITSELF", "status laundering")

        commitment = json.loads((out / "commitment.json").read_text(encoding="utf-8"))
        nonce = (out / "nonce.txt").read_text(encoding="utf-8")
        verify = subprocess.run(
            [
                sys.executable,
                str(COMMIT_VERIFY),
                str(out / "commitment.json"),
                str(out / "raw_result.bin"),
                nonce,
                "--challenge",
                str(challenge),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        expect(verify.returncode == 0 and "COMMITMENT VERIFIED" in verify.stdout, "commitment reveal failed")

        reused = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--challenge",
                str(challenge),
                "--output-dir",
                str(out),
                "--participant-id",
                "test-solver",
                "--participant-type",
                "separate-process-control",
                "--",
                sys.executable,
                str(solver),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        expect(reused.returncode != 0, "runner silently overwrote an existing frozen bundle")

    print("BLIND SOLVER RUNNER TESTS: 5/5 PASS")


if __name__ == "__main__":
    main()
