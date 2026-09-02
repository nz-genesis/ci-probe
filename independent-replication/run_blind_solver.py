#!/usr/bin/env python3
"""Run a blind solver through a separate local process and freeze the raw result.

This runner is provider-agnostic. It passes a minimal clean-room prompt plus the
exact frozen challenge to an arbitrary solver command over stdin, captures stdout
verbatim, and writes a local commitment bundle.

The runner does not establish material independence by itself. Independence must
be adjudicated from provenance and the actual execution path.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

PROTOCOL = "genesis-independent-replication-v1"
HASH_ALGORITHM = "SHA-256(raw_submission_bytes + newline + nonce_utf8)"
ROLE_CONTRACT = """Role: Independent systems-reasoning evaluator.
Solve the supplied frozen challenge from first principles.
Do not assume any predefined ontology, architecture, framework, primitive vocabulary, or expected answer.
Do not optimize for agreement with Genesis or any prior system.
Return a standalone raw result containing:
1. assumptions;
2. semantic distinctions;
3. smallest sufficient model/basis;
4. case coverage;
5. deletion/minimality analysis;
6. strongest counterexamples;
7. unresolved cases and uncertainty;
8. confidence.
A materially different or negative result is valid.
"""


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def commitment(raw: bytes, nonce: str) -> str:
    return sha256(raw + b"\n" + nonce.encode("utf-8"))


def invocation_digest(command: list[str]) -> str:
    # Bind provenance to the invocation without publishing potentially secret args.
    return sha256(b"\0".join(part.encode("utf-8") for part in command))


def prompt_bytes(challenge_bytes: bytes) -> bytes:
    return (
        ROLE_CONTRACT.encode("utf-8")
        + b"\n--- FROZEN CHALLENGE BYTES BEGIN ---\n"
        + challenge_bytes
        + b"\n--- FROZEN CHALLENGE BYTES END ---\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Run and freeze a clean-room blind solver")
    parser.add_argument("--challenge", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--participant-id", required=True)
    parser.add_argument("--participant-type", required=True)
    parser.add_argument("--provenance-note", default="")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="solver command after --")
    args = parser.parse_args()

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("solver command is required after --")

    challenge_bytes = args.challenge.read_bytes()
    challenge_sha = sha256(challenge_bytes)
    prompt = prompt_bytes(challenge_bytes)

    started = datetime.now(timezone.utc).isoformat()
    proc = subprocess.run(command, input=prompt, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    finished = datetime.now(timezone.utc).isoformat()
    if proc.returncode != 0:
        sys.stderr.buffer.write(proc.stderr)
        raise SystemExit(f"solver command failed with exit code {proc.returncode}")
    if not proc.stdout:
        raise SystemExit("solver produced empty stdout")

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=False)

    raw_path = output_dir / "raw_result.bin"
    raw_path.write_bytes(proc.stdout)

    stderr_path = output_dir / "solver_stderr.private.bin"
    stderr_path.write_bytes(proc.stderr)

    nonce = secrets.token_urlsafe(32)
    nonce_path = output_dir / "nonce.private.txt"
    nonce_path.write_text(nonce, encoding="utf-8")
    for private_path in (nonce_path, stderr_path):
        try:
            os.chmod(private_path, 0o600)
        except OSError:
            pass

    commitment_record = {
        "protocol": PROTOCOL,
        "challenge_sha256": challenge_sha,
        "submission_sha256": commitment(proc.stdout, nonce),
        "hash_algorithm": HASH_ALGORITHM,
    }
    (output_dir / "commitment.json").write_text(
        json.dumps(commitment_record, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    provenance = {
        "participant_id": args.participant_id,
        "participant_type": args.participant_type,
        "provenance_note": args.provenance_note,
        "challenge_path": str(args.challenge),
        "challenge_sha256": challenge_sha,
        "solver_executable": Path(command[0]).name,
        "solver_argument_count": max(len(command) - 1, 0),
        "solver_invocation_sha256": invocation_digest(command),
        "solver_command_arguments_published": False,
        "started_at_utc": started,
        "finished_at_utc": finished,
        "exit_code": proc.returncode,
        "raw_result_sha256": sha256(proc.stdout),
        "stderr_sha256": sha256(proc.stderr),
        "private_files": ["nonce.private.txt", "solver_stderr.private.bin"],
        "candidate_visibility": "NOT_ASSERTED_BY_RUNNER; MUST_BE DECLARED/ADJUDICATED SEPARATELY",
        "epistemic_status": "RAW_BLIND_RUN; NOT_EXTERNAL_INDEPENDENCE_BY_ITSELF",
    }
    (output_dir / "provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )

    print(f"BUNDLE_CREATED={output_dir}")
    print(f"challenge_sha256={challenge_sha}")
    print(f"raw_result_sha256={provenance['raw_result_sha256']}")
    print(f"submission_commitment={commitment_record['submission_sha256']}")
    print("PUBLISH commitment.json before revealing raw_result.bin and nonce.private.txt")
    print("DO NOT PUBLISH files marked private before the reveal stage")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
