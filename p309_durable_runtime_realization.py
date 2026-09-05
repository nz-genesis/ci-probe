"""P309: smallest faithful durable runtime realization.

Executable research fixture, not a production database. It uses SQLite WAL,
independent worker/observer processes, stable operation/effect identity,
explicit authority generations, and a provider stub with three contracts.
The worker crashes after an external effect but before durable acknowledgement;
recovery then reads durable state and attempts reconciliation.

Safety rule: an APPLIED_UNKNOWN result never becomes COMMITTED merely because
a later generation exists. A reconciliation observation must be bound to the
exact operation/effect identity and the current authority generation.
"""
from __future__ import annotations

import os
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

SCENARIOS = ("NON_IDEMPOTENT", "IDEMPOTENT", "RECONCILIABLE")


def db_open(path: str) -> sqlite3.Connection:
    db = sqlite3.connect(path, timeout=5, isolation_level=None)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA busy_timeout=5000")
    db.execute("CREATE TABLE IF NOT EXISTS state (k TEXT PRIMARY KEY, v TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS ops (operation_id TEXT PRIMARY KEY, effect_id TEXT NOT NULL, authority_epoch INTEGER NOT NULL, status TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS effects (effect_id TEXT PRIMARY KEY, count INTEGER NOT NULL)")
    return db


def provider_apply(db: sqlite3.Connection, contract: str, effect_id: str) -> str:
    row = db.execute("SELECT count FROM effects WHERE effect_id=?", (effect_id,)).fetchone()
    if row is None:
        db.execute("INSERT INTO effects(effect_id,count) VALUES(?,1)", (effect_id,))
        return "APPLIED_UNKNOWN"
    if contract == "NON_IDEMPOTENT":
        db.execute("UPDATE effects SET count=count+1 WHERE effect_id=?", (effect_id,))
        return "APPLIED_UNKNOWN"
    return "APPLIED"


def provider_observe(db: sqlite3.Connection, contract: str, effect_id: str) -> str:
    if contract == "NON_IDEMPOTENT":
        return "UNAVAILABLE"
    row = db.execute("SELECT count FROM effects WHERE effect_id=?", (effect_id,)).fetchone()
    return "APPLIED" if row and row[0] == 1 else "NOT_FOUND"


def worker(path: str, contract: str, phase: str) -> int:
    db = db_open(path)
    op = db.execute("SELECT operation_id,effect_id,authority_epoch,status FROM ops WHERE operation_id='op-1'").fetchone()
    if phase == "CRASH_AFTER_EFFECT":
        provider_apply(db, contract, op[1])
        os._exit(91)
    if phase == "RECOVER":
        epoch = int(db.execute("SELECT v FROM state WHERE k='authority_epoch'").fetchone()[0])
        # The original authorization is epoch 1. A rotated epoch cannot silently
        # adopt the old in-flight operation.
        if epoch != op[2]:
            db.close()
            return 0
        observation = provider_observe(db, contract, op[1])
        if observation == "APPLIED" and contract in ("IDEMPOTENT", "RECONCILIABLE"):
            db.execute("UPDATE ops SET status='COMMITTED' WHERE operation_id='op-1'")
        db.close()
        return 0
    db.close()
    return 12


def observer(path: str, expected_rotated: bool) -> int:
    db = db_open(path)
    epoch = int(db.execute("SELECT v FROM state WHERE k='authority_epoch'").fetchone()[0])
    status = db.execute("SELECT status FROM ops WHERE operation_id='op-1'").fetchone()[0]
    db.close()
    if expected_rotated:
        return 0 if (epoch == 2 and status == "IN_FLIGHT") else 20
    return 0 if (epoch == 1 and status in ("IN_FLIGHT", "COMMITTED")) else 21


def run_scenario(contract: str, rotate: bool) -> str:
    with tempfile.TemporaryDirectory(prefix="p309-") as td:
        path = str(Path(td) / "state.db")
        db = db_open(path)
        db.execute("INSERT INTO state VALUES('authority_epoch','1')")
        db.execute("INSERT INTO ops VALUES('op-1','effect-1',1,'IN_FLIGHT')")
        db.close()

        crashed = subprocess.run([sys.executable, __file__, "worker", path, contract, "CRASH_AFTER_EFFECT"], check=False)
        assert crashed.returncode == 91

        if rotate:
            db = db_open(path)
            db.execute("UPDATE state SET v='2' WHERE k='authority_epoch'")
            db.close()

        observer_process = subprocess.Popen([sys.executable, __file__, "observer", path, "1" if rotate else "0"])
        recovered = subprocess.run([sys.executable, __file__, "worker", path, contract, "RECOVER"], check=False)
        assert recovered.returncode == 0
        assert observer_process.wait() == 0

        db = db_open(path)
        count = db.execute("SELECT count FROM effects WHERE effect_id='effect-1'").fetchone()[0]
        status = db.execute("SELECT status FROM ops WHERE operation_id='op-1'").fetchone()[0]
        assert count == 1, (contract, rotate, count)
        expected = "IN_FLIGHT" if rotate or contract == "NON_IDEMPOTENT" else "COMMITTED"
        assert status == expected, (contract, rotate, status, expected)
        db.close()
        return status


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        raise SystemExit(worker(sys.argv[2], sys.argv[3], sys.argv[4]))
    if len(sys.argv) > 1 and sys.argv[1] == "observer":
        raise SystemExit(observer(sys.argv[2], bool(int(sys.argv[3]))))
    outcomes = {}
    for contract in SCENARIOS:
        outcomes[(contract, "ROTATED")] = run_scenario(contract, True)
        outcomes[(contract, "CURRENT")] = run_scenario(contract, False)
    assert outcomes[("NON_IDEMPOTENT", "CURRENT")] == "IN_FLIGHT"
    assert outcomes[("IDEMPOTENT", "CURRENT")] == "COMMITTED"
    assert outcomes[("RECONCILIABLE", "CURRENT")] == "COMMITTED"
    assert all(outcomes[(c, "ROTATED")] == "IN_FLIGHT" for c in SCENARIOS)
    print("P309 durable runtime realization: 6/6 PASS")
    print("crash/restart: PASS; independent observer process: PASS; stable effect identity: PASS")
    print("rotated authority blocks stale adoption: PASS; duplicate external effect: 0")
    print("current authority + observable provider contract: PASS")


if __name__ == "__main__":
    main()
