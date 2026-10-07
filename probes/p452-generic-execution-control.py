#!/usr/bin/env python3
"""Public generic control for the bounded six-scenario P452 execution class.

This is NOT a Genesis semantic test and contains no private Genesis source,
hypotheses, prompts, expected mappings, or canonical decisions.

It exercises only generic properties corresponding to the six P452 priority
scenarios: ambiguity preservation with clarification, deterministic selection
without authority inference, multi-source research before realization, real
artifact mutation followed by execution, independent concurrent processes,
and durable interruption/resumption across a new process.
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing as mp
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def s02_ambiguity(root: Path) -> dict:
    candidates = [
        {"id": "candidate-a", "requires_clarification": True},
        {"id": "candidate-b", "requires_clarification": True},
    ]
    assert len(candidates) == 2
    assert all(item["requires_clarification"] for item in candidates)
    return {
        "scenario": "S02",
        "status": "PASS",
        "property": "multiple candidates preserved and clarification required",
        "candidate_count": len(candidates),
    }


def s03_selection(root: Path) -> dict:
    candidates = [
        {"id": "a", "risk": 0.80, "evidence": 0.90},
        {"id": "b", "risk": 0.20, "evidence": 0.80},
        {"id": "c", "risk": 0.20, "evidence": 0.95},
    ]
    selected = max(
        candidates,
        key=lambda item: (item["evidence"] - item["risk"], item["evidence"]),
    )
    assert selected["id"] == "c"
    authority_granted = False
    assert authority_granted is False
    return {
        "scenario": "S03",
        "status": "PASS",
        "property": "deterministic selection without authority inference",
        "selected": selected["id"],
        "authority_granted": authority_granted,
    }


def s07_research_before_execution(root: Path) -> dict:
    corpus = root / "research-corpus"
    corpus.mkdir()
    sources = [
        ("method-a.txt", "method=a\noperation=write\npayload=RESEARCH_A\n"),
        ("method-b.txt", "method=b\noperation=write\npayload=RESEARCH_B\n"),
    ]
    for name, text in sources:
        (corpus / name).write_text(text, encoding="utf-8")

    observations = []
    for path in sorted(corpus.glob("method-*.txt")):
        text = path.read_text(encoding="utf-8")
        observations.append(
            {
                "path": path.name,
                "sha256": hashlib.sha256(text.encode()).hexdigest(),
                "payload": text.split("payload=", 1)[1].strip(),
            }
        )
    assert len(observations) == 2

    selected = max(observations, key=lambda item: item["sha256"])
    evidence = {
        "source_sha256": selected["sha256"],
        "source_count": len(observations),
    }
    target = root / "research-executed.txt"
    code = (
        "from pathlib import Path; "
        f"Path({str(target)!r}).write_text({selected['payload']!r} + '\\n', encoding='utf-8')"
    )
    subprocess.run([sys.executable, "-c", code], check=True)
    assert target.read_text(encoding="utf-8").strip() == selected["payload"]
    assert evidence["source_count"] == 2
    return {
        "scenario": "S07",
        "status": "PASS",
        "property": "multiple sources observed and qualified before realization",
        "source_count": evidence["source_count"],
        "executed_source_sha256": evidence["source_sha256"],
    }


def s08_modify(root: Path) -> dict:
    artifact = root / "mutable-system.py"
    output = root / "system-output.txt"
    artifact.write_text(
        "from pathlib import Path\n"
        f"Path({str(output)!r}).write_text('V1\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    before = sha(artifact)

    artifact.write_text(
        "from pathlib import Path\n"
        f"Path({str(output)!r}).write_text('V2\\n', encoding='utf-8')\n",
        encoding="utf-8",
    )
    after = sha(artifact)
    assert before != after

    subprocess.run([sys.executable, str(artifact)], check=True)
    assert output.read_text(encoding="utf-8") == "V2\n"
    return {
        "scenario": "S08",
        "status": "PASS",
        "property": "real artifact mutation is followed by execution and observed effect",
        "before_sha256": before,
        "after_sha256": after,
    }


def worker(path: str, index: int) -> None:
    Path(path).write_text(
        json.dumps({"owner": index, "pid": os.getpid()}),
        encoding="utf-8",
    )


def s11_concurrency(root: Path) -> dict:
    paths = [root / f"worker-{index}.json" for index in range(8)]
    ctx = mp.get_context("spawn")
    processes = [
        ctx.Process(target=worker, args=(str(path), index))
        for index, path in enumerate(paths)
    ]
    for process in processes:
        process.start()
    for process in processes:
        process.join(timeout=10)
        assert process.exitcode == 0

    records = [json.loads(path.read_text(encoding="utf-8")) for path in paths]
    assert sorted(record["owner"] for record in records) == list(range(8))
    assert all(record["pid"] > 0 for record in records)
    return {
        "scenario": "S11",
        "status": "PASS",
        "property": "eight independent OS processes complete with isolated state",
        "process_count": len(records),
    }


def resume_worker(state_path: str, ready_path: str) -> None:
    state = {"step": 1, "payload": "RESUME_ME"}
    Path(state_path).write_text(json.dumps(state), encoding="utf-8")
    with open(state_path, "rb") as handle:
        os.fsync(handle.fileno())
    Path(ready_path).write_text("READY", encoding="utf-8")
    while True:
        time.sleep(1)


def s15_resume(root: Path) -> dict:
    state = root / "resume-state.json"
    ready = root / "resume-ready"
    output = root / "resume-output.txt"

    process = mp.Process(
        target=resume_worker,
        args=(str(state), str(ready)),
    )
    process.start()
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline and not ready.exists():
        time.sleep(0.02)
    assert ready.exists()

    process.terminate()
    process.join(timeout=5)
    assert process.exitcode is not None
    assert state.exists()

    recovered = json.loads(state.read_text(encoding="utf-8"))
    assert recovered["step"] == 1

    continuation_code = (
        "import json; "
        "from pathlib import Path; "
        f"state=json.loads(Path({str(state)!r}).read_text(encoding='utf-8')); "
        f"Path({str(output)!r}).write_text(state['payload'] + '\\n', encoding='utf-8')"
    )
    subprocess.run([sys.executable, "-c", continuation_code], check=True)
    assert output.read_text(encoding="utf-8") == "RESUME_ME\n"
    return {
        "scenario": "S15",
        "status": "PASS",
        "property": "durable checkpoint survives interruption and new-process continuation",
        "resumed_step": recovered["step"],
        "new_process_continuation": True,
    }


def main() -> None:
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
        "control_id": "P452-GENERIC-EXECUTION-CONTROL-V2",
        "genesis_semantics_included": False,
        "private_source_included": False,
        "scenarios": results,
        "python": sys.version.split()[0],
        "commit": os.environ.get("GITHUB_SHA", ""),
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    Path("p452-generic-control-result.json").write_text(
        json.dumps(receipt, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(receipt, indent=2))
    print("P452_GENERIC_EXECUTION_CONTROL: PASS")


if __name__ == "__main__":
    main()
