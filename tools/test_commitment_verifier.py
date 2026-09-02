#!/usr/bin/env python3
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "tools" / "verify_commitment.py"


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def digest(raw: bytes, nonce: str) -> str:
    return sha256(raw + b"\n" + nonce.encode("utf-8"))


def run_case(raw: bytes, nonce: str, challenge_bytes: bytes, committed_challenge_bytes: bytes | None = None, mutate=False):
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        submission = root / "submission.bin"
        commitment = root / "commitment.json"
        challenge = root / "challenge.bin"
        submission.write_bytes(raw)
        challenge.write_bytes(challenge_bytes)
        committed = challenge_bytes if committed_challenge_bytes is None else committed_challenge_bytes
        commitment.write_text(json.dumps({
            "protocol": "genesis-independent-replication-v1",
            "challenge_sha256": sha256(committed),
            "submission_sha256": digest(raw, nonce),
            "hash_algorithm": "SHA-256(raw_submission_bytes + newline + nonce_utf8)",
        }), encoding="utf-8")
        if mutate:
            submission.write_bytes(raw + b"tampered")
        return subprocess.run(
            [sys.executable, str(VERIFIER), str(commitment), str(submission), nonce, "--challenge", str(challenge)],
            capture_output=True, text=True, check=False,
        )


def expect(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    challenge = b"frozen challenge bytes\n"
    valid = run_case(b"independent result\n", "nonce-1", challenge)
    expect(valid.returncode == 0 and "COMMITMENT VERIFIED" in valid.stdout, "valid reveal failed")

    tampered = run_case(b"original\n", "nonce-2", challenge, mutate=True)
    expect(tampered.returncode != 0 and "commitment mismatch" in tampered.stderr, "tampered submission accepted")

    wrong_challenge = run_case(b"result\n", "nonce-3", challenge, b"different challenge\n")
    expect(wrong_challenge.returncode != 0 and "challenge hash mismatch" in wrong_challenge.stderr, "wrong challenge accepted")

    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        submission = root / "submission.bin"
        commitment = root / "commitment.json"
        actual_challenge = root / "challenge.bin"
        raw = b"result\n"
        submission.write_bytes(raw)
        actual_challenge.write_bytes(challenge)
        commitment.write_text(json.dumps({
            "protocol": "genesis-independent-replication-v1",
            "challenge_sha256": sha256(challenge),
            "submission_sha256": digest(raw, "nonce-4"),
            "hash_algorithm": "SHA-256(raw_submission_bytes + newline + nonce_utf8)",
        }), encoding="utf-8")
        wrong_nonce = subprocess.run(
            [sys.executable, str(VERIFIER), str(commitment), str(submission), "wrong", "--challenge", str(actual_challenge)],
            capture_output=True, text=True, check=False,
        )
    expect(wrong_nonce.returncode != 0 and "commitment mismatch" in wrong_nonce.stderr, "wrong nonce accepted")
    print("COMMITMENT VERIFIER TESTS: 4/4 PASS")


if __name__ == "__main__":
    main()
