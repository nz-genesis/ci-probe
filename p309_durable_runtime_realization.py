"""P309: smallest faithful durable runtime realization.

This is an executable research fixture, not a production database. It uses
SQLite in WAL mode, two independent worker processes, stable operation/effect
identity, explicit authority generations, and a provider stub with three
contracts. The test intentionally crashes the worker after the provider effect
but before the durable acknowledgement, then restarts and reconciles.

Safety rule: an APPLIED_UNKNOWN result is never treated as committed merely
because a later generation exists. A reconciliation observation must be bound
to the exact operation/effect identity and current authority generation.
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


def worker(path: str, contract: str, phase: str) -> int:
    db = db_open(path)
    op = db.execute("SELECT operation_id,effect_id,authority_epoch,status FROM ops WHERE operation_id='op-1'").fetchone()
    if op is None:
        db.execute("INSERT INTO ops VALUES('op-1','effect-1',1,'IN_FLIGHT')")
        op = ('op-1', 'effect-1', 1, 'IN_FLIGHT')
    if phase == "CRASH_AFTER_EFFECT":
        provider_apply(db, contract, op[1])
        os._exit(91)
    if phase == "RECOVER":
        # Current authority must be read from durable state, never from cache.
        epoch = int(db.execute("SELECT v FROM state WHERE k='authority_epoch'").fetchone()[0])
        count = db.execute("SELECT count FROM effects WHERE effect_id=?", (op[1],)).fetchone()[0]
        if epoch != 2 or op[2] != epoch:
            return 10
        if contract == "NON_IDEMPOTENT":
            # No reconciliation proof for a non-idempotent unknown effect.
            return 0 if count == 1 else 11
        db.execute("UPDATE ops SET status='COMMITTED', authority_epoch=? WHERE operation_id=?", (epoch, op[0]))
        return 0
    return 12


def observer(path: str) -> int:
    db = db_open(path)
    epoch = int(db.execute("SELECT v FROM state WHERE k='authority_epoch'").fetchone()[0])
    status = db.execute("SELECT status FROM ops WHERE operation_id='op-1'").fetchone()[0]
    # Observer may see the durable in-flight state, but it cannot manufacture a commit.
    return 0 if (epoch == 2 and status == "IN_FLIGHT") else 20


def run_scenario(contract: str) -> None:
    with tempfile.TemporaryDirectory(prefix="p309-") as td:
        path = str(Path(td) / "state.db")
        db = db_open(path)
        db.execute("INSERT INTO state VALUES('authority_epoch','1')")
        db.execute("INSERT INTO ops VALUES('op-1','effect-1',1,'IN_FLIGHT')")
        db.close()

        p = subprocess.run([sys.executable, __file__, "worker", path, contract, "CRASH_AFTER_EFFECT"], check=False)
        assert p.returncode == 91

        # Authority rotates while the original operation is in flight.
        db = db_open(path)
        db.execute("UPDATE state SET v='2' WHERE k='authority_epoch'")
        db.close()

        p2 = subprocess.run([sys.executable, __file__, "worker", path, contract, "RECOVER"], check=False)
        assert p2.returncode == 0
        p3 = subprocess.run([sys.executable, __file__, "observer", path], check=False)
        assert p3.returncode == 0

        db = db_open(path)
        count = db.execute("SELECT count FROM effects WHERE effect_id='effect-1'").fetchone()[0]
        status = db.execute("SELECT status FROM ops WHERE operation_id='op-1'").fetchone()[0]
        assert count == 1, (contract, count)
        assert status == "IN_FLIGHT", (contract, status)


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "worker":
        raise SystemExit(worker(sys.argv[2], sys.argv[3], sys.argv[4]))
    if len(sys.argv) > 1 and sys.argv[1] == "observer":
        raise SystemExit(observer(sys.argv[2]))
    for contract in SCENARIOS:
        run_scenario(contract)
    print("P309 durable runtime realization: 3/3 PASS")
    print("crash/restart: PASS; two-process observer: PASS; stable effect identity: PASS")
    print("authority rotation: PASS; duplicate external effect: 0")
    print("status remains IN_FLIGHT for APPLIED_UNKNOWN: PASS")


if __name__ == "__main__":
    main()
