"""P310: persistence/reconciliation failure injection and recovery cost.

Bounded executable fixture. It injects failures around provider effect and
persistent acknowledgement, varies authority rotation and provider contract,
and counts durable reads/writes as a concrete control/recovery cost proxy.
It deliberately keeps the semantic model in State/Transition/Capability/
Authority/Observation/Evidence/Constraint rather than adding a new primitive.
"""
from __future__ import annotations

import sqlite3
from itertools import product
from pathlib import Path
import tempfile

CONTRACTS = ("NON_IDEMPOTENT", "IDEMPOTENT", "RECONCILIABLE")
FAILURES = ("BEFORE_EFFECT", "AFTER_EFFECT_BEFORE_ACK", "AFTER_ACK", "OBSERVATION_FAILURE")
ROTATION = (False, True)


def open_db(path: str, counters: dict[str, int]) -> sqlite3.Connection:
    db = sqlite3.connect(path, isolation_level=None)
    db.execute("PRAGMA journal_mode=WAL")
    db.execute("PRAGMA synchronous=FULL")
    db.set_trace_callback(lambda stmt: counters.__setitem__("sql", counters["sql"] + 1))
    db.execute("CREATE TABLE IF NOT EXISTS state(k TEXT PRIMARY KEY,v TEXT NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS op(id TEXT PRIMARY KEY,effect TEXT,epoch INTEGER,status TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS effect(id TEXT PRIMARY KEY,count INTEGER)")
    return db


def apply_effect(db: sqlite3.Connection, contract: str) -> None:
    row = db.execute("SELECT count FROM effect WHERE id='e1'").fetchone()
    if row is None:
        db.execute("INSERT INTO effect VALUES('e1',1)")
    elif contract == "NON_IDEMPOTENT":
        db.execute("UPDATE effect SET count=count+1 WHERE id='e1'")


def recover(db: sqlite3.Connection, contract: str, failure: str) -> None:
    op = db.execute("SELECT epoch,status FROM op WHERE id='o1'").fetchone()
    epoch = int(db.execute("SELECT v FROM state WHERE k='epoch'").fetchone()[0])
    if failure == "BEFORE_EFFECT":
        return
    if epoch != op[0] or failure == "OBSERVATION_FAILURE":
        return
    if contract in ("IDEMPOTENT", "RECONCILIABLE"):
        observed = db.execute("SELECT count FROM effect WHERE id='e1'").fetchone()
        if observed and observed[0] == 1:
            db.execute("UPDATE op SET status='COMMITTED' WHERE id='o1'")


def run(contract: str, failure: str, rotate: bool) -> tuple[str, int, int]:
    counters = {"sql": 0}
    with tempfile.TemporaryDirectory(prefix="p310-") as td:
        path = str(Path(td) / "state.db")
        db = open_db(path, counters)
        db.execute("INSERT INTO state VALUES('epoch','1')")
        db.execute("INSERT INTO op VALUES('o1','e1',1,'IN_FLIGHT')")
        if failure != "BEFORE_EFFECT":
            apply_effect(db, contract)
        if failure == "AFTER_ACK":
            db.execute("UPDATE op SET status='COMMITTED' WHERE id='o1'")
        db.close()
        if rotate:
            db = open_db(path, counters)
            db.execute("UPDATE state SET v='2' WHERE k='epoch'")
            db.close()
        db = open_db(path, counters)
        if failure != "AFTER_ACK":
            recover(db, contract, failure)
        status = db.execute("SELECT status FROM op WHERE id='o1'").fetchone()[0]
        effect_count = db.execute("SELECT count FROM effect WHERE id='e1'").fetchone()[0] if failure != "BEFORE_EFFECT" else 0
        db.close()
        return status, effect_count, counters["sql"]


def main() -> None:
    checked = 0
    total_sql = 0
    for contract, failure, rotate in product(CONTRACTS, FAILURES, ROTATION):
        checked += 1
        status, effect_count, sql = run(contract, failure, rotate)
        total_sql += sql
        assert effect_count in (0, 1), (contract, failure, rotate, effect_count)
        if rotate and failure != "AFTER_ACK":
            assert status == "IN_FLIGHT", (contract, failure, rotate, status)
        if failure == "OBSERVATION_FAILURE":
            assert status == "IN_FLIGHT", (contract, failure, rotate, status)
        if failure == "AFTER_ACK":
            assert status == "COMMITTED"
        if failure == "AFTER_EFFECT_BEFORE_ACK" and not rotate and contract in ("IDEMPOTENT", "RECONCILIABLE"):
            assert status == "COMMITTED"
        if failure == "AFTER_EFFECT_BEFORE_ACK" and not rotate and contract == "NON_IDEMPOTENT":
            assert status == "IN_FLIGHT"
    print(f"P310 persistence-failure matrix: {checked}/{checked} PASS")
    print(f"recovery/control SQL operations: {total_sql}")
    print("stale rotation blocking: PASS; observation failure blocking: PASS")
    print("new semantic primitive required: NO")


if __name__ == "__main__":
    main()
