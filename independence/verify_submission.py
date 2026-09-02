#!/usr/bin/env python3
"""Deterministic structural verifier for BFV blind submissions.

The verifier deliberately knows nothing about Genesis primitives or target
factorization. It checks corpus binding, opaque factor identifiers, complete
coverage, duplicate/conflicting rows, and deterministic canonicalization.
Semantic adjudication is intentionally outside this public tool.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SUPPORTED_PROTOCOLS = {"BFV-1", "BFV-2"}
FACTOR_RE = re.compile(r"^F[0-9]{3}$")
OBLIGATION_RE = re.compile(r"^O[0-9]{3}$")


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def fail(message: str) -> int:
    print(f"FAIL: {message}")
    return 1


def verify(corpus_path: Path, submission_path: Path) -> int:
    try:
        corpus = json.loads(corpus_path.read_text(encoding="utf-8"))
        submission = json.loads(submission_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return fail(f"invalid JSON/input: {exc}")

    if not isinstance(corpus, dict) or corpus.get("protocol_version") not in SUPPORTED_PROTOCOLS:
        return fail("corpus protocol_version must be a supported BFV version")
    protocol_version = corpus["protocol_version"]
    obligations = corpus.get("obligations")
    if not isinstance(obligations, list) or not obligations:
        return fail("corpus must contain a non-empty obligations list")

    obligation_ids = []
    for item in obligations:
        if not isinstance(item, dict) or set(item) != {"obligation_id", "text"}:
            return fail("each corpus obligation must contain only obligation_id and text")
        oid = item["obligation_id"]
        if not isinstance(oid, str) or not OBLIGATION_RE.fullmatch(oid):
            return fail(f"invalid obligation id: {oid!r}")
        if not isinstance(item["text"], str) or not item["text"].strip():
            return fail(f"empty obligation text: {oid}")
        obligation_ids.append(oid)
    if len(set(obligation_ids)) != len(obligation_ids):
        return fail("corpus contains duplicate obligation ids")

    if not isinstance(submission, dict):
        return fail("submission must be a JSON object")
    if submission.get("protocol_version") != protocol_version:
        return fail("submission protocol_version does not match corpus")
    if submission.get("protocol_version") not in SUPPORTED_PROTOCOLS:
        return fail("submission protocol_version is not supported")

    expected_sha = sha256_file(corpus_path)
    if submission.get("corpus_sha256") != expected_sha:
        return fail("corpus_sha256 does not match the frozen corpus")

    factors = submission.get("factors")
    coverage = submission.get("coverage")
    if not isinstance(factors, list) or not factors:
        return fail("submission factors must be a non-empty list")
    if not isinstance(coverage, list) or not coverage:
        return fail("submission coverage must be a non-empty list")

    factor_ids = []
    for factor in factors:
        if not isinstance(factor, dict) or set(factor) != {"factor_id"}:
            return fail("factor entries must contain only factor_id")
        fid = factor["factor_id"]
        if not isinstance(fid, str) or not FACTOR_RE.fullmatch(fid):
            return fail(f"factor id is not opaque BFV form: {fid!r}")
        factor_ids.append(fid)
    if len(set(factor_ids)) != len(factor_ids):
        return fail("duplicate factor ids")
    factor_set = set(factor_ids)

    seen: dict[str, tuple[str, ...]] = {}
    for row in coverage:
        if not isinstance(row, dict) or set(row) != {"obligation_id", "factor_ids"}:
            return fail("coverage rows must contain only obligation_id and factor_ids")
        oid = row["obligation_id"]
        fids = row["factor_ids"]
        if oid not in obligation_ids:
            return fail(f"coverage references unknown obligation: {oid}")
        if not isinstance(fids, list) or not fids:
            return fail(f"coverage for {oid} must contain at least one factor")
        if any(not isinstance(fid, str) or not FACTOR_RE.fullmatch(fid) for fid in fids):
            return fail(f"coverage for {oid} contains invalid factor id")
        if any(fid not in factor_set for fid in fids):
            return fail(f"coverage for {oid} references undeclared factor")
        normalized = tuple(sorted(set(fids)))
        if len(normalized) != len(fids):
            return fail(f"coverage for {oid} contains duplicate factor ids")
        if oid in seen and seen[oid] != normalized:
            return fail(f"conflicting duplicate coverage for {oid}")
        if oid in seen:
            return fail(f"duplicate coverage row for {oid}")
        seen[oid] = normalized

    missing = sorted(set(obligation_ids) - set(seen))
    if missing:
        return fail("missing coverage for: " + ", ".join(missing))

    canonical = {
        "protocol_version": protocol_version,
        "corpus_sha256": expected_sha,
        "factors": [{"factor_id": fid} for fid in sorted(factor_set)],
        "coverage": [
            {"obligation_id": oid, "factor_ids": list(seen[oid])}
            for oid in sorted(seen)
        ],
    }
    digest = hashlib.sha256(canonical_json(canonical)).hexdigest()
    print("PASS: structural blind-submission contract")
    print(f"protocol_version={protocol_version}")
    print(f"corpus_sha256={expected_sha}")
    print(f"factor_count={len(factor_set)}")
    print(f"obligation_count={len(obligation_ids)}")
    print(f"canonical_submission_sha256={digest}")
    print("semantic_status=NOT_ADJUDICATED")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("corpus", type=Path)
    parser.add_argument("submission", type=Path)
    args = parser.parse_args()
    return verify(args.corpus, args.submission)


if __name__ == "__main__":
    sys.exit(main())
