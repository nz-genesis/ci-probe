import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "tools" / "verify_commitment.py"


def commitment(raw: bytes, nonce: str) -> str:
    return hashlib.sha256(raw + b"\n" + nonce.encode("utf-8")).hexdigest()


def run_verifier(commitment_path: Path, submission_path: Path, nonce: str, challenge_sha: str):
    return subprocess.run(
        [
            sys.executable,
            str(VERIFIER),
            str(commitment_path),
            str(submission_path),
            nonce,
            "--challenge-sha",
            challenge_sha,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def write_case(tmp_path, raw: bytes, nonce: str, challenge_sha: str):
    submission = tmp_path / "submission.bin"
    submission.write_bytes(raw)
    record = {
        "protocol": "genesis-independent-replication-v1",
        "challenge_sha256": challenge_sha,
        "submission_sha256": commitment(raw, nonce),
        "hash_algorithm": "SHA-256(raw_submission_bytes + newline + nonce_utf8)",
    }
    commitment_path = tmp_path / "commitment.json"
    commitment_path.write_text(json.dumps(record), encoding="utf-8")
    return commitment_path, submission


def test_valid_reveal_verifies(tmp_path):
    challenge = "a" * 64
    nonce = "random-test-nonce"
    commitment_path, submission = write_case(tmp_path, b"independent result\n", nonce, challenge)
    result = run_verifier(commitment_path, submission, nonce, challenge)
    assert result.returncode == 0
    assert "COMMITMENT VERIFIED" in result.stdout


def test_tampered_submission_fails(tmp_path):
    challenge = "b" * 64
    nonce = "another-test-nonce"
    commitment_path, submission = write_case(tmp_path, b"original\n", nonce, challenge)
    submission.write_bytes(b"tampered\n")
    result = run_verifier(commitment_path, submission, nonce, challenge)
    assert result.returncode != 0
    assert "commitment mismatch" in result.stderr


def test_wrong_challenge_binding_fails(tmp_path):
    challenge = "c" * 64
    nonce = "binding-test-nonce"
    commitment_path, submission = write_case(tmp_path, b"result\n", nonce, challenge)
    result = run_verifier(commitment_path, submission, nonce, "d" * 64)
    assert result.returncode != 0
    assert "challenge hash mismatch" in result.stderr


def test_wrong_nonce_fails(tmp_path):
    challenge = "e" * 64
    commitment_path, submission = write_case(tmp_path, b"result\n", "correct", challenge)
    result = run_verifier(commitment_path, submission, "wrong", challenge)
    assert result.returncode != 0
    assert "commitment mismatch" in result.stderr
