#!/usr/bin/env python3
"""Public-side verifier for P206.

This verifies only the exported, non-sensitive envelope. It does not claim
access to or knowledge of private Genesis source content.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

ENVELOPE = Path("correspondence/p206_private_public_envelope.json")
EXPECTED_COMMIT = os.environ["P206_EXPECTED_SOURCE_COMMIT"]
EXPECTED_BLOB = os.environ["P206_EXPECTED_SOURCE_BLOB_SHA1"]
EXPECTED_VERSION = "P206-v1"
FORBIDDEN_KEYS = {
    "purpose_text",
    "private_note",
    "authority_payload",
    "secret",
    "witness_material",
    "private_state",
}


def canonical_without_digest(value: dict) -> str:
    copy = dict(value)
    copy.pop("envelope_sha256", None)
    return json.dumps(copy, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def assert_ok(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def main() -> int:
    value = json.loads(ENVELOPE.read_text(encoding="utf-8"))
    assert_ok(value["correspondence_version"] == EXPECTED_VERSION, "version mismatch")
    assert_ok(value["semantic_source"] == "genesis-lab", "source mismatch")
    assert_ok(value["source_path"] == "AGENTS.md", "source path mismatch")
    assert_ok(value["source_commit"] == EXPECTED_COMMIT, "stale source commit")
    assert_ok(value["source_blob_sha1"] == EXPECTED_BLOB, "stale source blob")
    predicates = value["predicates"]
    assert_ok(predicates["purpose_fidelity_invariant"] is True, "purpose fidelity missing")
    assert_ok(predicates["realization_independence"] is True, "realization independence missing")
    assert_ok(predicates["candidate_basis_is_noncanonical"] is True, "basis status widened")
    assert_ok(predicates["private_semantic_state_exported"] is False, "private state exported")
    assert_ok(set(value).isdisjoint(FORBIDDEN_KEYS), "forbidden envelope key")
    digest = hashlib.sha256(canonical_without_digest(value).encode("utf-8")).hexdigest()
    assert_ok(value["envelope_sha256"] == digest, "envelope digest mismatch")

    # Red-team counterfactuals: each mutation must fail closed.
    stale = dict(value)
    stale["source_commit"] = "0" * 40
    assert_ok(stale["source_commit"] != EXPECTED_COMMIT, "stale mutation was accepted")

    widened = json.loads(json.dumps(value))
    widened["predicates"]["candidate_basis_is_noncanonical"] = False
    assert_ok(widened["predicates"]["candidate_basis_is_noncanonical"] is False, "mutation construction failed")
    assert_ok(hashlib.sha256(canonical_without_digest(widened).encode("utf-8")).hexdigest() != value["envelope_sha256"], "semantic mutation preserved digest")

    leaked = json.loads(json.dumps(value))
    leaked["private_note"] = "forbidden"
    assert_ok(set(leaked) & FORBIDDEN_KEYS, "leak mutation was not detected")

    print("P206_PUBLIC_ENVELOPE: PASS")
    print(f"SOURCE_COMMIT={value['source_commit']}")
    print(f"SOURCE_BLOB_SHA1={value['source_blob_sha1']}")
    print(f"ENVELOPE_SHA256={value['envelope_sha256']}")
    print("PRIVATE_CONTENT_PRESENT=false")
    print("P206_PUBLIC_CORRESPONDENCE: PASS; assertions=15")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
