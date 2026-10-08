#!/usr/bin/env python3
"""Regression tests for verify_blind_bundle.py using only the Python stdlib."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / "independent-replication" / "verify_blind_bundle.py"
CHALLENGE = ROOT / "independent-replication" / "challenge-v3.json"
EXPECTED_CHALLENGE_SHA256 = "913c162ede3741ead44dca3efe3fbbf33f5de764254d6a2da88cc90cf08b05a"


def write_bundle(bundle: Path, raw: bytes = b"independent raw result\n", nonce: str = "nonce-1") -> None:
    import hashlib

    raw_sha = hashlib.sha256(raw).hexdigest()
    commitment = hashlib.sha256(raw + b"\n" + nonce.encode()).hexdigest()
    bundle.mkdir()
    (bundle / "raw_result.bin").write_bytes(raw)
    (bundle / "nonce.private.txt").write_text(nonce, encoding="utf-8")
    (bundle / "commitment.json").write_text(json.dumps({
        "protocol": "genesis-independent-replication-v1",
        "challenge_sha256": EXPECTED_CHALLENGE_SHA256,
        "submission_sha256": commitment,
        "hash_algorithm": "SHA-256(raw_submission_bytes + newline + nonce_utf8)",
    }) + "\n", encoding="utf-8")
    (bundle / "provenance.json").write_text(json.dumps({
        "challenge_sha256": EXPECTED_CHALLENGE_SHA256,
        "raw_result_sha256": raw_sha,
        "exit_code": 0,
        "candidate_visibility": "NOT_ASSERTED_BY_RUNNER; MUST_BE DECLARED/ADJUDICATED SEPARATELY",
        "epistemic_status": "RAW_BLIND_RUN; NOT_EXTERNAL_INDEPENDENCE_BY_ITSELF",
    }) + "\n", encoding="utf-8")


def run(bundle: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--challenge", str(CHALLENGE), "--bundle", str(bundle)],
        text=True, capture_output=True, check=False,
    )


def test_valid_bundle() -> None:
    with TemporaryDirectory() as td:
        bundle = Path(td) / "bundle"
        write_bundle(bundle)
        result = run(bundle)
        assert result.returncode == 0, result.stderr
        assert "IR_V3_BUNDLE=VALID" in result.stdout
        assert "MATERIAL_EXTERNAL_INDEPENDENCE=NOT_ESTABLISHED" in result.stdout


def test_tampered_raw_is_rejected() -> None:
    with TemporaryDirectory() as td:
        bundle = Path(td) / "bundle"
        write_bundle(bundle)
        (bundle / "raw_result.bin").write_bytes(b"tampered\n")
        result = run(bundle)
        assert result.returncode != 0
        assert "submission commitment does not match" in result.stderr


def test_wrong_challenge_identity_is_rejected() -> None:
    with TemporaryDirectory() as td:
        bundle = Path(td) / "bundle"
        write_bundle(bundle)
        (bundle / "commitment.json").write_text(
            json.dumps({
                "challenge_sha256": "0" * 64,
                "submission_sha256": "0" * 64,
            }),
            encoding="utf-8",
        )
        result = run(bundle)
        assert result.returncode != 0
        assert "commitment challenge_sha256 mismatch" in result.stderr


def test_non_raw_epistemic_status_is_rejected() -> None:
    with TemporaryDirectory() as td:
        bundle = Path(td) / "bundle"
        write_bundle(bundle)
        provenance = json.loads((bundle / "provenance.json").read_text())
        provenance["epistemic_status"] = "ATTESTED_EXECUTION"
        (bundle / "provenance.json").write_text(json.dumps(provenance), encoding="utf-8")
        result = run(bundle)
        assert result.returncode != 0
        assert "raw blind run" in result.stderr


if __name__ == "__main__":
    for test_fn in (
        test_valid_bundle,
        test_tampered_raw_is_rejected,
        test_wrong_challenge_identity_is_rejected,
        test_non_raw_epistemic_status_is_rejected,
    ):
        test_fn()
    print("PASS: IR-V3 bundle admission validator regression tests")
