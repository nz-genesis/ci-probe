#!/usr/bin/env python3
"""Generic fail-closed frozen-corpus provenance gate.

Public-safe control implementation. It validates only mechanical integrity and
claim-to-source span binding; it does not contain Genesis-specific semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

SCHEMA = "generic-provenance-v1"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError("JSON root must be an object")
    return value


def load_jsonl(path: Path) -> list[dict]:
    rows: list[dict] = []
    try:
        with path.open("r", encoding="utf-8") as fh:
            for line_no, raw in enumerate(fh, 1):
                if not raw.strip():
                    continue
                value = json.loads(raw)
                if not isinstance(value, dict):
                    raise ValueError(f"row {line_no} is not an object")
                rows.append(value)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"invalid JSONL: {exc}") from exc
    return rows


def inside(root: Path, candidate: Path) -> bool:
    try:
        candidate.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def verify(manifest_path: Path, claims_path: Path, corpus_root: Path) -> dict:
    errors: list[str] = []
    try:
        manifest = load_json(manifest_path)
    except ValueError as exc:
        return {"schema": SCHEMA, "status": "FAIL", "errors": [str(exc)]}

    if manifest.get("schema") != SCHEMA:
        errors.append("manifest schema mismatch")
    sources = manifest.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("manifest sources must be a non-empty list")
        sources = []

    index: dict[str, dict] = {}
    for source in sources:
        if not isinstance(source, dict):
            errors.append("malformed source entry")
            continue
        sid, rel, expected = source.get("source_id"), source.get("path"), source.get("sha256")
        if not all(isinstance(x, str) and x for x in (sid, rel, expected)):
            errors.append("malformed source fields")
            continue
        if sid in index:
            errors.append(f"duplicate source_id: {sid}")
        index[sid] = source
        if len(expected) != 64 or any(c not in "0123456789abcdef" for c in expected):
            errors.append(f"invalid sha256: {sid}")
            continue
        path = corpus_root / rel
        if not inside(corpus_root, path):
            errors.append(f"source escapes corpus root: {sid}")
            continue
        if not path.is_file():
            errors.append(f"missing source: {sid}")
            continue
        if sha256_file(path) != expected:
            errors.append(f"hash mismatch: {sid}")

    try:
        claims = load_jsonl(claims_path)
    except ValueError as exc:
        errors.append(str(exc))
        claims = []

    seen: set[str] = set()
    for claim in claims:
        required = ("claim_id", "source_id", "start_line", "end_line", "exact_span", "claim")
        if any(k not in claim for k in required):
            errors.append(f"malformed claim: {claim.get('claim_id', '<unknown>')}")
            continue
        cid = claim["claim_id"]
        if not isinstance(cid, str) or not cid:
            errors.append("claim_id must be a non-empty string")
            continue
        if cid in seen:
            errors.append(f"duplicate claim_id: {cid}")
        seen.add(cid)
        sid = claim["source_id"]
        if not isinstance(sid, str) or sid not in index:
            errors.append(f"{cid}: unknown source_id")
            continue
        start, end = claim["start_line"], claim["end_line"]
        if (isinstance(start, bool) or not isinstance(start, int) or
                isinstance(end, bool) or not isinstance(end, int) or start < 1 or end < start):
            errors.append(f"{cid}: invalid line range")
            continue
        if not isinstance(claim["claim"], str) or not claim["claim"].strip():
            errors.append(f"{cid}: empty/non-string claim")
            continue
        if not isinstance(claim["exact_span"], str):
            errors.append(f"{cid}: exact_span must be a string")
            continue
        path = corpus_root / index[sid]["path"]
        if not inside(corpus_root, path):
            errors.append(f"{cid}: source escapes corpus root")
            continue
        try:
            lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        except (OSError, UnicodeError) as exc:
            errors.append(f"{cid}: source unreadable as UTF-8: {exc}")
            continue
        if end > len(lines):
            errors.append(f"{cid}: line range exceeds source")
            continue
        actual = "".join(lines[start - 1:end])
        if actual != claim["exact_span"]:
            errors.append(f"{cid}: exact_span mismatch")

    return {"schema": SCHEMA, "status": "PASS" if not errors else "FAIL",
            "source_count": len(sources), "claim_count": len(claims), "errors": errors,
            "not_proven": ["semantic equivalence", "model faithfulness", "external knowledge absence", "actor independence"]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--claims", type=Path, required=True)
    ap.add_argument("--corpus", type=Path, required=True)
    args = ap.parse_args()
    result = verify(args.manifest, args.claims, args.corpus)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
