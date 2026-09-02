import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).parent
VALIDATOR=ROOT/"validate_attestation.py"

def base():
    return {
        "attestation_version":"1","participant_id":"p1","participant_type":"external",
        "challenge_id":"IR-V2","challenge_sha256":"0"*64,"prompt_contract_sha256":"1"*64,
        "model_family":"test","model_version_or_provider_declared_id":"test-v1",
        "runtime_name":"test","runtime_version":"1","solver_artifact_digest":"2"*64,
        "configuration_digest":"3"*64,"execution_started_at":"2026-01-01T00:00:00Z",
        "execution_finished_at":"2026-01-01T00:01:00Z","raw_result_sha256":"4"*64,
        "commitment_sha256":"5"*64,"prior_genesis_exposure":"no",
        "genesis_operator_relationship":"external","epistemic_status":"ATTESTED_EXECUTION"
    }

def run(obj, challenge=None):
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"a.json"; p.write_text(json.dumps(obj), encoding="utf-8")
        cmd=[sys.executable,str(VALIDATOR),str(p)]
        if challenge: cmd += ["--challenge",str(challenge)]
        return subprocess.run(cmd,capture_output=True,text=True)

class AttestationValidatorTests(unittest.TestCase):
    def test_valid_structure(self):
        r=run(base()); self.assertEqual(r.returncode,0,r.stderr)

    def test_missing_field_fails_closed(self):
        a=base(); del a["raw_result_sha256"]
        self.assertNotEqual(run(a).returncode,0)

    def test_malformed_hash_fails(self):
        a=base(); a["raw_result_sha256"]="not-a-hash"
        self.assertNotEqual(run(a).returncode,0)

    def test_unknown_field_fails(self):
        a=base(); a["secret_dump"]="should-not-be-accepted"
        self.assertNotEqual(run(a).returncode,0)

    def test_l4_requires_external_participant(self):
        a=base(); a["independence_level"]="L4"; a["participant_type"]="affiliated"
        self.assertNotEqual(run(a).returncode,0)

    def test_l4_requires_no_prior_exposure(self):
        a=base(); a["independence_level"]="L4"; a["prior_genesis_exposure"]="unknown"
        self.assertNotEqual(run(a).returncode,0)

    def test_l4_requires_external_relationship(self):
        a=base(); a["independence_level"]="L4"; a["genesis_operator_relationship"]="unknown"
        self.assertNotEqual(run(a).returncode,0)

    def test_challenge_digest_is_checked_when_file_supplied(self):
        with tempfile.TemporaryDirectory() as d:
            challenge=Path(d)/"challenge.bin"; challenge.write_bytes(b"frozen")
            a=base(); a["challenge_sha256"]=hashlib.sha256(b"wrong").hexdigest()
            self.assertNotEqual(run(a,challenge).returncode,0)

    def test_missing_challenge_file_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            a=base(); self.assertNotEqual(run(a,Path(d)/"missing.bin").returncode,0)

    def test_invalid_datetime_fails(self):
        a=base(); a["execution_started_at"]="tomorrow"
        self.assertNotEqual(run(a).returncode,0)

    def test_unknown_is_not_upgraded_to_l4(self):
        a=base(); a["independence_level"]="L3"; a["participant_type"]="unknown"; a["prior_genesis_exposure"]="unknown"; a["genesis_operator_relationship"]="unknown"
        self.assertEqual(run(a).returncode,0)

if __name__ == "__main__": unittest.main(verbosity=2)
