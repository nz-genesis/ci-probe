#!/usr/bin/env python3
"""Ontology-agnostic structural verifier for IR-V1 submissions."""
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
TOPICS = ["authority", "evidence", "identity", "provenance", "execution", "relation"]


def fail(msg):
    print("FAIL: " + msg)
    return 1


def main():
    p = argparse.ArgumentParser()
    p.add_argument("submission")
    p.add_argument(
        "--challenge",
        default=str(Path(__file__).with_name("challenge-v1.json")),
        help="Frozen challenge file used for this verification",
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

    if challenge.get("challenge_id") != "IR-V1":
        return fail("wrong challenge")

    challenge_sha = hashlib.sha256(challenge_path.read_bytes()).hexdigest()
    declared_sha = str(submission["challenge_sha256"]).lower()
    if declared_sha != challenge_sha:
        return fail("challenge_sha256 does not match supplied frozen challenge")

    basis = submission["basis"]
    if not isinstance(basis, list) or not basis:
        return fail("basis must be non-empty list")
    ids = [item.get("id") for item in basis if isinstance(item, dict)]
    if len(ids) != len(basis) or len(set(ids)) != len(ids) or any(not item for item in ids):
        return fail("basis ids must be unique")

    cases = {item["id"] for item in challenge["cases"]}
    mapped = set()
    for mapping in submission["case_mappings"]:
        if not all(key in mapping for key in ("case_id", "basis_ids", "justification")):
            return fail("invalid case mapping")
        if mapping["case_id"] not in cases:
            return fail("unknown case id")
        if not mapping["basis_ids"] or not set(mapping["basis_ids"]).issubset(ids):
            return fail("mapping references unknown basis")
        if not str(mapping["justification"]).strip():
            return fail("empty justification")
        mapped.add(mapping["case_id"])
    if mapped != cases:
        return fail("not all cases mapped")

    deletions = submission["deletion_analysis"]
    deletion_ids = {item.get("basis_id") for item in deletions if isinstance(item, dict)}
    if deletion_ids != set(ids):
        return fail("deletion analysis must cover every basis item")
    if any(not str(item.get("justification", "")).strip() for item in deletions):
        return fail("empty deletion justification")

    counterexamples = submission["counterexamples"]
    if not isinstance(counterexamples, list):
        return fail("counterexamples must be a list")
    seen_topics = set()
    for item in counterexamples:
        if not isinstance(item, dict):
            return fail("counterexamples must use structured records")
        if not all(key in item for key in ("topic", "scenario", "failure_if_ignored")):
            return fail("counterexample requires topic, scenario, failure_if_ignored")
        topic = str(item["topic"]).strip().lower()
        if topic in TOPICS:
            seen_topics.add(topic)
        if not str(item["scenario"]).strip() or not str(item["failure_if_ignored"]).strip():
            return fail("counterexample scenario/failure cannot be empty")
    missing_topics = set(TOPICS) - seen_topics
    if missing_topics:
        return fail("counterexample coverage missing: " + ", ".join(sorted(missing_topics)))

    if not str(submission["uncertainty"]).strip() or not str(submission["provenance"]).strip():
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
    print("NOTE semantic adequacy and agreement with any target hypothesis are not judged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
