import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).parent
VALIDATOR=ROOT/"validate_attestation.py"
CHALLENGE=ROOT/"challenge-v2.json"

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
    import tempfile
    with tempfile.TemporaryDirectory() as d:
        p=Path(d)/"a.json"; p.write_text(json.dumps(obj))
        cmd=[sys.executable,str(VALIDATOR),str(p)]
        if challenge: cmd += ["--challenge",str(challenge)]
        return subprocess.run(cmd,capture_output=True,text=True)

def test_valid_structure():
    r=run(base())
    assert r.returncode==0, r.stderr

def test_missing_field_fails_closed():
    a=base(); del a["raw_result_sha256"]
    assert run(a).returncode != 0

def test_malformed_hash_fails():
    a=base(); a["raw_result_sha256"]="not-a-hash"
    assert run(a).returncode != 0

def test_unknown_field_fails():
    a=base(); a["secret_dump"]="should-not-be-accepted"
    assert run(a).returncode != 0

def test_l4_requires_external_participant():
    a=base(); a["independence_level"]="L4"; a["participant_type"]="affiliated"
    assert run(a).returncode != 0

def test_l4_requires_no_prior_exposure():
    a=base(); a["independence_level"]="L4"; a["prior_genesis_exposure"]="unknown"
    assert run(a).returncode != 0

def test_l4_requires_external_relationship():
    a=base(); a["independence_level"]="L4"; a["genesis_operator_relationship"]="unknown"
    assert run(a).returncode != 0

def test_challenge_digest_is_checked_when_file_supplied(tmp_path):
    challenge=tmp_path/"challenge.bin"; challenge.write_bytes(b"frozen")
    a=base(); import hashlib; a["challenge_sha256"]=hashlib.sha256(b"wrong").hexdigest()
    assert run(a,challenge).returncode != 0

def test_unknown_is_not_upgraded_to_l4():
    a=base(); a["independence_level"]="L3"; a["participant_type"]="unknown"; a["prior_genesis_exposure"]="unknown"; a["genesis_operator_relationship"]="unknown"
    assert run(a).returncode==0
