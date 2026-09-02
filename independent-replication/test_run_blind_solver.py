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
        secret_arg = "SECRET_ARGUMENT_MUST_NOT_BE_PUBLISHED"
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
                "--public-provenance-note",
                "public test metadata",
                "--",
                sys.executable,
                str(solver),
                secret_arg,
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        expect(result.returncode == 0, f"runner failed: {result.stderr}")
        expect((out / "raw_result.bin").read_bytes() == b"blind-result-v1\n", "raw output changed")

        provenance_text = (out / "provenance.json").read_text(encoding="utf-8")
        provenance = json.loads(provenance_text)
        expect(provenance["challenge_sha256"] == sha256(challenge_bytes), "challenge digest mismatch")
        expect(provenance["raw_result_sha256"] == sha256(b"blind-result-v1\n"), "raw digest mismatch")
        expect(provenance["epistemic_status"] == "RAW_BLIND_RUN; NOT_EXTERNAL_INDEPENDENCE_BY_ITSELF", "status laundering")
        expect(provenance["solver_command_arguments_published"] is False, "command publication flag incorrect")
        expect(secret_arg not in provenance_text, "secret-like command argument leaked")
        expect("solver_invocation_sha256" not in provenance, "raw command digest retained")
        expect(provenance["public_provenance_note"] == "public test metadata", "public provenance note lost")
        expect((out / "nonce.private.txt").exists(), "private nonce missing")
        expect((out / "solver_stderr.private.bin").exists(), "private stderr file missing")

        nonce = (out / "nonce.private.txt").read_text(encoding="utf-8")
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

        failing_solver = tmp / "failing_solver.py"
        failing_secret = "SECRET_FROM_SOLVER_STDERR"
        failing_solver.write_text(
            "import sys\n"
            f"sys.stderr.write('{failing_secret}\\n')\n"
            "raise SystemExit(23)\n",
            encoding="utf-8",
        )
        failed_out = tmp / "failed-bundle"
        failed = subprocess.run(
            [
                sys.executable,
                str(RUNNER),
                "--challenge",
                str(challenge),
                "--output-dir",
                str(failed_out),
                "--participant-id",
                "failing-solver",
                "--participant-type",
                "separate-process-control",
                "--",
                sys.executable,
                str(failing_solver),
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        expect(failed.returncode != 0, "failing solver was accepted")
        expect(failing_secret not in failed.stderr and failing_secret not in failed.stdout, "solver stderr secret leaked")
        expect("stderr_sha256=" in failed.stderr, "failure stderr digest not reported")
        expect(not failed_out.exists(), "failed run created a misleading frozen bundle")

    print("BLIND SOLVER RUNNER TESTS: 17/17 PASS")


if __name__ == "__main__":
    main()
