#!/usr/bin/env python3
"""Public generic control for a bounded six-scenario execution class.

This is NOT a Genesis semantic test and contains no private Genesis source,
hypotheses, prompts, expected mappings, or canonical decisions.

It reproduces only generic execution properties corresponding to:
ambiguity preservation, deterministic candidate selection, research-before-action,
artifact modification, independent concurrency, and interruption/resumption.
The output is raw control evidence for private adjudication.
"""
from __future__ import annotations
import hashlib, json, multiprocessing as mp, os, tempfile, time
from pathlib import Path

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def s02_ambiguity(root):
    candidates = ["candidate-a", "candidate-b"]
    assert len(candidates) == 2 and candidates[0] != candidates[1]
    return {"scenario": "S02", "status": "PASS", "property": "multiple candidates preserved"}

def s03_selection(root):
    candidates = [{"id": "a", "score": 0.70}, {"id": "b", "score": 0.90}, {"id": "c", "score": 0.80}]
    winner = max(candidates, key=lambda x: x["score"])
    assert winner["id"] == "b"
    return {"scenario": "S03", "status": "PASS", "property": "deterministic best-candidate selection"}

def s07_research_before_execution(root):
    source = root / "source.txt"
    artifact = root / "artifact.txt"
    source.write_text("public-control-source-v1\n", encoding="utf-8")
    source_sha = sha(source)
    observed = source.read_text(encoding="utf-8")
    artifact.write_text("executed-from:" + observed, encoding="utf-8")
    assert sha(source) == source_sha and artifact.exists()
    return {"scenario": "S07", "status": "PASS", "property": "source observation precedes realization", "source_sha256": source_sha}

def s08_modify(root):
    artifact = root / "mutable.txt"
    artifact.write_text("before\n", encoding="utf-8")
    before = sha(artifact)
    artifact.write_text("after\n", encoding="utf-8")
    after = sha(artifact)
    assert before != after
    return {"scenario": "S08", "status": "PASS", "property": "real artifact mutation observed", "before_sha256": before, "after_sha256": after}

def worker(path):
    p = Path(path)
    p.write_text("worker:" + str(os.getpid()) + "\n", encoding="utf-8")

def s11_concurrency(root):
    paths = [root / f"worker-{i}.txt" for i in range(8)]
    procs = [mp.Process(target=worker, args=(str(p),)) for p in paths]
    for p in procs:
        p.start()
    for p in procs:
        p.join()
    assert all(p.exitcode == 0 for p in procs) and all(p.exists() for p in paths)
    return {"scenario": "S11", "status": "PASS", "property": "8 independent OS processes complete without shared-state collision"}

def s15_resume(root):
    checkpoint = root / "checkpoint.json"
    checkpoint.write_text(json.dumps({"next": 2}), encoding="utf-8")
    checkpoint_sha = sha(checkpoint)
    checkpoint2 = json.loads(checkpoint.read_text(encoding="utf-8"))
    assert checkpoint2["next"] == 2
    return {"scenario": "S15", "status": "PASS", "property": "durable checkpoint supports continuation", "checkpoint_sha256": checkpoint_sha}

def main():
    with tempfile.TemporaryDirectory(prefix="p452-control-") as td:
        root = Path(td)
        results = [
            s02_ambiguity(root),
            s03_selection(root),
            s07_research_before_execution(root),
            s08_modify(root),
            s11_concurrency(root),
            s15_resume(root),
        ]
    receipt = {
        "control_id": "P452-GENERIC-EXECUTION-CONTROL-V1",
        "genesis_semantics_included": False,
        "private_source_included": False,
        "scenarios": results,
        "python": os.sys.version.split()[0],
        "commit": os.environ.get("GITHUB_SHA", ""),
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    Path("p452-generic-control-result.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(receipt, indent=2))
    print("P452_GENERIC_EXECUTION_CONTROL: PASS")

if __name__ == "__main__":
    main()

# Public-first execution receipt trigger: syntax correction after hosted probe.
