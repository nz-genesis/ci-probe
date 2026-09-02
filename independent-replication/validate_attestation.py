#!/usr/bin/env python3
"""Fail-closed structural validator for External Execution Attestation v1.

This validator checks declared structure and locally available integrity data.
It deliberately does not treat self-attested metadata as proof of actor
independence or semantic correctness.
"""
from __future__ import annotations
import argparse, hashlib, json, re, sys
from datetime import datetime
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
ENUMS = {
    "participant_type": {"external", "affiliated", "unknown"},
    "prior_genesis_exposure": {"yes", "no", "unknown"},
    "genesis_operator_relationship": {"external", "affiliated", "unknown"},
    "epistemic_status": {"ATTESTED_EXECUTION", "RAW_BLIND_RUN", "UNKNOWN"},
    "independence_level": {"L1", "L2", "L3", "L4"},
}

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
        if key in a and (not isinstance(a[key],str) or not HEX64.fullmatch(a[key])):
            errors.append(f"{key} must be lowercase SHA-256")
    for key, allowed in ENUMS.items():
        if key in a and a[key] not in allowed: errors.append(f"invalid {key}")
    for key in ("execution_started_at", "execution_finished_at"):
        if key in a:
            try: datetime.fromisoformat(a[key].replace("Z", "+00:00"))
            except (TypeError, ValueError): errors.append(f"{key} must be ISO-8601 date-time")
    if challenge is not None:
        if not challenge.is_file():
            errors.append(f"challenge file does not exist: {challenge}")
        elif "challenge_sha256" in a:
            actual=sha256_file(challenge)
            if a["challenge_sha256"] != actual:
                errors.append(f"challenge SHA mismatch: declared {a['challenge_sha256']} actual {actual}")
    # L4 is a claim requiring corroborating evidence outside this structural
    # document. The validator never upgrades a self-attestation into proof.
    if a.get("independence_level") == "L4":
        if a.get("participant_type") != "external": errors.append("L4 declaration requires participant_type=external")
        if a.get("prior_genesis_exposure") != "no": errors.append("L4 declaration requires prior_genesis_exposure=no")
        if a.get("genesis_operator_relationship") != "external": errors.append("L4 declaration requires genesis_operator_relationship=external")
    return errors

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("attestation", type=Path)
    p.add_argument("--challenge", type=Path)
    args=p.parse_args()
    try: a=json.loads(args.attestation.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"ATTESTATION_INVALID: invalid JSON: {e}", file=sys.stderr); return 1
    if not isinstance(a,dict):
        print("ATTESTATION_INVALID: top-level value must be an object", file=sys.stderr); return 1
    errors=validate(a,args.challenge)
    if errors:
        print("ATTESTATION_INVALID:", file=sys.stderr)
        for e in errors: print(f"- {e}", file=sys.stderr)
        return 1
    print("ATTESTATION_VALID: structural checks passed")
    if a.get("independence_level") == "L4":
        print("L4_DECLARATION: requires independent corroboration; this validator does not establish actor independence")
    print("NOTE: structural validity does not establish semantic correctness or material external independence")
    return 0

if __name__ == "__main__": raise SystemExit(main())
