#!/usr/bin/env python3
"""Target-ontology-agnostic structural verifier for IR-V2 submissions."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

REQ = [
    "challenge_sha256",
    "basis",
    "case_mappings",
    "deletion_analysis",
    "counterexamples",
    "uncertainty",
    "provenance",
    "candidate_visibility",
]


def fail(msg):
    print("FAIL: " + msg)
    return 1


def nonempty_text(value):
    return isinstance(value, str) and bool(value.strip())


def main():
    p = argparse.ArgumentParser()
    p.add_argument("submission")
    p.add_argument(
        "--challenge",
        default=str(Path(__file__).with_name("challenge-v2.json")),
        help="Frozen neutral challenge file used for this verification",
    )
    args = p.parse_args()

    try:
        submission = json.loads(Path(args.submission).read_text(encoding="utf-8"))
        challenge_path = Path(args.challenge)
        challenge = json.loads(challenge_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return fail("invalid JSON: " + str(exc))

    for key in REQ:
        if key not in submission:
            return fail("missing field: " + key)

    if challenge.get("challenge_id") != "IR-V2":
        return fail("wrong challenge")

    challenge_sha = hashlib.sha256(challenge_path.read_bytes()).hexdigest()
    if str(submission["challenge_sha256"]).lower() != challenge_sha:
        return fail("challenge_sha256 does not match supplied frozen challenge")

    basis = submission["basis"]
    if not isinstance(basis, list) or not basis:
        return fail("basis must be non-empty list")
    if any(not isinstance(item, dict) for item in basis):
        return fail("basis entries must be objects")
    ids = [item.get("id") for item in basis]
    if any(not nonempty_text(item_id) for item_id in ids) or len(set(ids)) != len(ids):
        return fail("basis ids must be unique non-empty strings")
    if any(not nonempty_text(item.get("description")) for item in basis):
        return fail("basis descriptions must be non-empty strings")

    cases = {item["id"] for item in challenge.get("cases", []) + challenge.get("adversarial_cases", [])}
    mappings = submission["case_mappings"]
    if not isinstance(mappings, list):
        return fail("case_mappings must be a list")
    mapped = set()
    for mapping in mappings:
        if not isinstance(mapping, dict) or not all(k in mapping for k in ("case_id", "basis_ids", "justification")):
            return fail("invalid case mapping")
        case_id = mapping["case_id"]
        basis_ids = mapping["basis_ids"]
        if case_id not in cases:
            return fail("unknown case id")
        if case_id in mapped:
            return fail("duplicate case mapping")
        if not isinstance(basis_ids, list) or not basis_ids or not set(basis_ids).issubset(ids):
            return fail("case mapping basis_ids invalid")
        if not nonempty_text(mapping["justification"]):
            return fail("empty justification")
        mapped.add(case_id)
    if mapped != cases:
        return fail("not all cases mapped")

    deletions = submission["deletion_analysis"]
    if not isinstance(deletions, list):
        return fail("deletion_analysis must be a list")
    deletion_ids = set()
    for item in deletions:
        if not isinstance(item, dict) or not all(k in item for k in ("basis_id", "cases_lost_if_removed", "justification")):
            return fail("invalid deletion analysis")
        basis_id = item["basis_id"]
        lost_cases = item["cases_lost_if_removed"]
        if basis_id not in ids or basis_id in deletion_ids:
            return fail("invalid or duplicate deletion basis id")
        if not isinstance(lost_cases, list) or any(case_id not in cases for case_id in lost_cases):
            return fail("cases_lost_if_removed must contain known case ids")
        if not nonempty_text(item["justification"]):
            return fail("empty deletion justification")
        deletion_ids.add(basis_id)
    if deletion_ids != set(ids):
        return fail("deletion analysis must cover every basis item exactly once")

    counterexamples = submission["counterexamples"]
    if not isinstance(counterexamples, list):
        return fail("counterexamples must be a list")
    for item in counterexamples:
        if not isinstance(item, dict) or not all(k in item for k in ("domain", "scenario", "failure_if_ignored")):
            return fail("counterexample requires domain, scenario, failure_if_ignored")
        if not all(nonempty_text(item[k]) for k in ("domain", "scenario", "failure_if_ignored")):
            return fail("counterexample fields cannot be empty")

    if not nonempty_text(submission["uncertainty"]) or not nonempty_text(submission["provenance"]):
        return fail("uncertainty/provenance required")
    if not isinstance(submission["candidate_visibility"], (str, bool)):
        return fail("candidate_visibility must be explicit")

    print("PASS schema")
    print("PASS frozen_challenge_sha256=" + challenge_sha)
    print(f"PASS case_coverage={len(cases)}/{len(cases)}")
    print(f"PASS deletion_coverage={len(ids)}/{len(ids)}")
    print("PASS structured_counterexamples")
    print("PASS uncertainty_provenance")
    print("PASS candidate_visibility")
    print("NOTE semantic adequacy, target agreement, and category coverage are not judged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
