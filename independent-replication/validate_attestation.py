#!/usr/bin/env python3
"""Fail-closed validator for External Execution Attestation v1.

The validator checks schema-independent structural invariants without claiming
that metadata proves actor independence or semantic correctness.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from pathlib import Path

HEX64 = re.compile(r"^[0-9a-f]{64}$")
REQUIRED = {
    "attestation_version", "participant_id", "participant_type", "challenge_id",
    "challenge_sha256", "prompt_contract_sha256", "model_family",
    "model_version_or_provider_declared_id", "runtime_name", "runtime_version",
    "solver_artifact_digest", "configuration_digest", "execution_started_at",
    "execution_finished_at", "raw_result_sha256", "commitment_sha256",
    "prior_genesis_exposure", "genesis_operator_relationship", "epistemic_status",
}
ALLOWED = REQUIRED | {"independence_level", "notes"}

def fail(msg: str) -> int:
    print(f"ATTESTATION_INVALID: {msg}", file=sys.stderr)
    return 1

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def validate(a: dict, challenge: Path | None) -> list[str]:
    errors=[]
    missing=REQUIRED-set(a)
    if missing: errors.append("missing required fields: " + ", ".join(sorted(missing)))
    unknown=set(a)-ALLOWED
    if unknown: errors.append("unknown fields: " + ", ".join(sorted(unknown)))
    if a.get("attestation_version") != "1": errors.append("attestation_version must be 1")
    for key in ["challenge_sha256","prompt_contract_sha256","solver_artifact_digest","configuration_digest","raw_result_sha256","commitment_sha256"]:
        if key in a and (not isinstance(a[key],str) or not HEX64.fullmatch(a[key])): errors.append(f"{key} must be lowercase SHA-256")
    if a.get("participant_type") not in {"external","affiliated","unknown"}: errors.append("invalid participant_type")
    if a.get("prior_genesis_exposure") not in {"yes","no","unknown"}: errors.append("invalid prior_genesis_exposure")
    if a.get("genesis_operator_relationship") not in {"external","affiliated","unknown"}: errors.append("invalid genesis_operator_relationship")
    if a.get("epistemic_status") not in {"ATTESTED_EXECUTION","RAW_BLIND_RUN","UNKNOWN"}: errors.append("invalid epistemic_status")
    if challenge and challenge.exists() and "challenge_sha256" in a:
        actual=sha256_file(challenge)
        if a["challenge_sha256"] != actual: errors.append(f"challenge SHA mismatch: declared {a['challenge_sha256']} actual {actual}")
    if a.get("independence_level") == "L4":
        if a.get("participant_type") != "external": errors.append("L4 requires participant_type=external")
        if a.get("prior_genesis_exposure") != "no": errors.append("L4 requires prior_genesis_exposure=no")
        if a.get("genesis_operator_relationship") != "external": errors.append("L4 requires genesis_operator_relationship=external")
    return errors

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("attestation", type=Path)
    p.add_argument("--challenge", type=Path)
    args=p.parse_args()
    try: a=json.loads(args.attestation.read_text(encoding="utf-8"))
    except Exception as e: return fail(f"invalid JSON: {e}")
    if not isinstance(a,dict): return fail("top-level value must be an object")
    errors=validate(a,args.challenge)
    if errors:
        for e in errors: print(f"- {e}", file=sys.stderr)
        return 1
    print("ATTESTATION_VALID: structural checks passed")
    print("NOTE: structural validity does not establish semantic correctness or material external independence")
    return 0

if __name__ == "__main__": raise SystemExit(main())
