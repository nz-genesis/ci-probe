"""Generic single-host SQLite operation-journal boundary probe.

This public probe tests database mechanics only. It contains no private product
code, provider adapter, credentials, network calls, or real external service.
A local marker file is used only to distinguish the journal from an independent
local side-effect fixture; it is not provider integration evidence.
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing
import os
from pathlib import Path
import queue
import sqlite3
import tempfile
import time
from typing import Any

DB_NAME = "operation-journal.sqlite3"
BUSY_TIMEOUT_MS = 15_000


def connect(path: str) -> sqlite3.Connection:
    db = sqlite3.connect(path, timeout=BUSY_TIMEOUT_MS / 1000, isolation_level=None)
    db.execute(f"PRAGMA busy_timeout={BUSY_TIMEOUT_MS}")
    db.execute("PRAGMA synchronous=FULL")
    db.execute("PRAGMA foreign_keys=ON")
    return db


def initialize(path: str) -> tuple[str, int]:
    db = connect(path)
    try:
        mode = str(db.execute("PRAGMA journal_mode=WAL").fetchone()[0]).lower()
        synchronous = int(db.execute("PRAGMA synchronous").fetchone()[0])
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS operation (
                operation_id TEXT PRIMARY KEY,
                principal_namespace TEXT NOT NULL,
                caller_namespace TEXT NOT NULL,
                operation_family TEXT NOT NULL,
                operation_version TEXT NOT NULL,
                idempotency_key_digest TEXT NOT NULL,
                semantic_digest TEXT NOT NULL,
                status TEXT NOT NULL CHECK (
                    status IN (
                        'CLAIMED',
                        'DISPATCH_COMMITTED',
                        'UNKNOWN',
                        'OBSERVED',
                        'VERIFIED'
                    )
                ),
                dispatch_attempts INTEGER NOT NULL DEFAULT 0,
                created_at_ns INTEGER NOT NULL,
                updated_at_ns INTEGER NOT NULL,
                UNIQUE (
                    principal_namespace,
                    caller_namespace,
                    operation_family,
                    operation_version,
                    idempotency_key_digest
                )
            )
            """
        )
        db.execute(
            "CREATE INDEX IF NOT EXISTS operation_status_idx ON operation(status)"
        )
        return mode, synchronous
    finally:
        db.close()


def canonical_digest(value: Any) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def operation_identity(
    principal: str,
    caller: str,
    family: str,
    version: str,
    idempotency_key: str,
) -> tuple[str, str]:
    key_digest = hashlib.sha256(idempotency_key.encode("utf-8")).hexdigest()
    namespace = {
        "principal": principal,
        "caller": caller,
        "family": family,
        "version": version,
    }
    operation_id = canonical_digest([namespace, key_digest])
    return operation_id, key_digest


def claim(
    path: str,
    principal: str,
    caller: str,
    family: str,
    version: str,
    idempotency_key: str,
    semantic_digest: str,
) -> tuple[str, str]:
    operation_id, key_digest = operation_identity(
        principal, caller, family, version, idempotency_key
    )
    now = time.time_ns()
    db = connect(path)
    try:
        # Acquire the writer reservation before reading the unique key. This
        # serializes competing writers across independent local processes.
        db.execute("BEGIN IMMEDIATE")
        row = db.execute(
            """
            SELECT operation_id, semantic_digest
              FROM operation
             WHERE principal_namespace = ?
               AND caller_namespace = ?
               AND operation_family = ?
               AND operation_version = ?
               AND idempotency_key_digest = ?
            """,
            (principal, caller, family, version, key_digest),
        ).fetchone()
        if row is not None:
            db.execute("COMMIT")
            if row[1] != semantic_digest:
                return "CONFLICT", str(row[0])
            return "EXISTING", str(row[0])

        db.execute(
            """
            INSERT INTO operation (
                operation_id, principal_namespace, caller_namespace,
                operation_family, operation_version, idempotency_key_digest,
                semantic_digest, status, dispatch_attempts,
                created_at_ns, updated_at_ns
            ) VALUES (?, ?, ?, ?, ?, ?, ?, 'CLAIMED', 0, ?, ?)
            """,
            (
                operation_id,
                principal,
                caller,
                family,
                version,
                key_digest,
                semantic_digest,
                now,
                now,
            ),
        )
        db.execute("COMMIT")
        return "CREATED", operation_id
    except BaseException:
        if db.in_transaction:
            db.execute("ROLLBACK")
        raise
    finally:
        db.close()


def claim_worker(
    path: str,
    start: multiprocessing.synchronize.Event,
    results: multiprocessing.queues.Queue,
    index: int,
) -> None:
    start.wait(20)
    outcome, operation_id = claim(
        path,
        "principal-A",
        "caller-A",
        "generation",
        "v1",
        "same-key",
        "digest-A",
    )
    results.put((index, outcome, operation_id))


def insert_then_exit_before_commit(path: str) -> None:
    operation_id, key_digest = operation_identity(
        "principal-crash", "caller-crash", "write", "v1", "uncommitted-key"
    )
    db = connect(path)
    db.execute("BEGIN IMMEDIATE")
    db.execute(
        """
        INSERT INTO operation (
            operation_id, principal_namespace, caller_namespace,
            operation_family, operation_version, idempotency_key_digest,
            semantic_digest, status, dispatch_attempts,
            created_at_ns, updated_at_ns
        ) VALUES (?, 'principal-crash', 'caller-crash', 'write', 'v1',
                  ?, 'digest-crash', 'CLAIMED', 0, 1, 1)
        """,
        (operation_id, key_digest),
    )
    # Abrupt process termination with an uncommitted transaction.
    os._exit(73)


def commit_dispatch_barrier_then_exit(
    path: str, operation_id: str, marker_path: str | None
) -> None:
    db = connect(path)
    try:
        db.execute("BEGIN IMMEDIATE")
        changed = db.execute(
            """
            UPDATE operation
               SET status = 'DISPATCH_COMMITTED',
                   dispatch_attempts = dispatch_attempts + 1,
                   updated_at_ns = ?
             WHERE operation_id = ? AND status = 'CLAIMED'
            """,
            (time.time_ns(), operation_id),
        ).rowcount
        if changed != 1:
            raise AssertionError("dispatch barrier was not committed exactly once")
        db.execute("COMMIT")
    finally:
        db.close()

    if marker_path is not None:
        marker = Path(marker_path)
        fd = os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
        try:
            os.write(fd, b"local-fixture-effect\n")
            os.fsync(fd)
        finally:
            os.close(fd)
        directory_fd = os.open(str(marker.parent), os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)

    # Simulate process loss after the durable barrier and optional local marker,
    # but before any acknowledgement/result observation is persisted.
    os._exit(74)


def read_operation(path: str, operation_id: str) -> tuple[str, int] | None:
    db = connect(path)
    try:
        row = db.execute(
            "SELECT status, dispatch_attempts FROM operation WHERE operation_id = ?",
            (operation_id,),
        ).fetchone()
        return (str(row[0]), int(row[1])) if row else None
    finally:
        db.close()


def recovery_classification(status: str) -> str:
    if status == "CLAIMED":
        return "READY_BEFORE_DISPATCH"
    if status in {"DISPATCH_COMMITTED", "UNKNOWN"}:
        return "UNKNOWN_REQUIRES_RECONCILIATION"
    if status == "VERIFIED":
        return "VERIFIED"
    return "NOT_VERIFIED"


def integrity_check(path: str) -> str:
    db = connect(path)
    try:
        return str(db.execute("PRAGMA integrity_check").fetchone()[0])
    finally:
        db.close()


def run() -> dict[str, Any]:
    ctx = multiprocessing.get_context("spawn")
    with tempfile.TemporaryDirectory(prefix="sqlite-journal-probe-") as directory:
        db_path = str(Path(directory) / DB_NAME)
        mode, synchronous = initialize(db_path)
        assert mode == "wal", mode
        assert synchronous == 2, synchronous  # SQLite FULL

        # Real independent processes race to claim the same scoped key.
        worker_count = 12
        start = ctx.Event()
        results = ctx.Queue()
        workers = [
            ctx.Process(target=claim_worker, args=(db_path, start, results, i))
            for i in range(worker_count)
        ]
        for worker in workers:
            worker.start()
        start.set()
        for worker in workers:
            worker.join(30)
        assert all(not worker.is_alive() for worker in workers), "worker timeout"
        assert all(worker.exitcode == 0 for worker in workers), [
            worker.exitcode for worker in workers
        ]
        raced = [results.get(timeout=10) for _ in range(worker_count)]
        outcomes = [item[1] for item in raced]
        operation_ids = {item[2] for item in raced}
        assert outcomes.count("CREATED") == 1, outcomes
        assert outcomes.count("EXISTING") == worker_count - 1, outcomes
        assert len(operation_ids) == 1, operation_ids
        shared_operation_id = next(iter(operation_ids))

        # Same key with different semantics conflicts; it does not create a
        # second operation or change the original digest.
        conflict, conflict_id = claim(
            db_path, "principal-A", "caller-A", "generation", "v1",
            "same-key", "digest-B"
        )
        assert conflict == "CONFLICT"
        assert conflict_id == shared_operation_id

        # The same raw key in a different principal/caller/family/version
        # namespace is a distinct operation, not a cross-tenant collision.
        namespace_ids = set()
        for principal, caller, family, version in (
            ("principal-B", "caller-A", "generation", "v1"),
            ("principal-A", "caller-B", "generation", "v1"),
            ("principal-A", "caller-A", "analysis", "v1"),
            ("principal-A", "caller-A", "generation", "v2"),
        ):
            outcome, operation_id = claim(
                db_path, principal, caller, family, version, "same-key", "digest-A"
            )
            assert outcome == "CREATED"
            namespace_ids.add(operation_id)
        assert len(namespace_ids) == 4
        assert shared_operation_id not in namespace_ids

        # Abrupt exit before transaction commit must not publish a partial row.
        before_id, _ = operation_identity(
            "principal-crash", "caller-crash", "write", "v1", "uncommitted-key"
        )
        child = ctx.Process(target=insert_then_exit_before_commit, args=(db_path,))
        child.start()
        child.join(20)
        assert child.exitcode == 73, child.exitcode
        assert read_operation(db_path, before_id) is None
        assert integrity_check(db_path) == "ok"

        # Crash after durable dispatch barrier but before any observation:
        # even when the local marker is absent, recovery must remain UNKNOWN.
        no_effect_outcome, no_effect_id = claim(
            db_path, "principal-C", "caller-C", "write", "v1",
            "barrier-no-effect", "digest-C"
        )
        assert no_effect_outcome == "CREATED"
        child = ctx.Process(
            target=commit_dispatch_barrier_then_exit,
            args=(db_path, no_effect_id, None),
        )
        child.start()
        child.join(20)
        assert child.exitcode == 74
        status, attempts = read_operation(db_path, no_effect_id) or ("MISSING", -1)
        assert recovery_classification(status) == "UNKNOWN_REQUIRES_RECONCILIATION"
        assert attempts == 1

        # Crash after an independent local marker is durable but before the
        # journal records observation. The journal still cannot claim success
        # and recovery must not dispatch again.
        effect_outcome, effect_id = claim(
            db_path, "principal-D", "caller-D", "write", "v1",
            "barrier-with-marker", "digest-D"
        )
        assert effect_outcome == "CREATED"
        marker_path = str(Path(directory) / "independent-local-marker")
        child = ctx.Process(
            target=commit_dispatch_barrier_then_exit,
            args=(db_path, effect_id, marker_path),
        )
        child.start()
        child.join(20)
        assert child.exitcode == 74
        assert Path(marker_path).read_bytes() == b"local-fixture-effect\n"
        status, attempts = read_operation(db_path, effect_id) or ("MISSING", -1)
        assert recovery_classification(status) == "UNKNOWN_REQUIRES_RECONCILIATION"
        assert attempts == 1

        # The raw idempotency key is not stored in the database. Check the DB
        # and its sidecar files after checkpointing the WAL.
        db = connect(db_path)
        try:
            db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        finally:
            db.close()
        database_files = list(Path(directory).glob(DB_NAME + "*"))
        assert database_files
        assert all(b"same-key" not in file.read_bytes() for file in database_files)

        assert integrity_check(db_path) == "ok"

        return {
            "status": "PASS",
            "python_version": __import__("sys").version.split()[0],
            "sqlite_version": sqlite3.sqlite_version,
            "journal_mode": mode,
            "synchronous": "FULL",
            "processes": worker_count,
            "same_key_race": {
                "created": outcomes.count("CREATED"),
                "existing": outcomes.count("EXISTING"),
                "operation_identity_count": len(operation_ids),
            },
            "same_key_different_digest": conflict,
            "namespace_isolation_count": len(namespace_ids),
            "crash_before_commit": "uncommitted_row_absent",
            "crash_after_dispatch_barrier_before_observation": "UNKNOWN",
            "crash_after_local_marker_before_observation": "UNKNOWN_NO_REDISPATCH",
            "raw_idempotency_key_persisted": False,
            "integrity_check": "ok",
            "scope": "single-host local SQLite file; no network filesystem or multi-host claim",
            "external_effect_limit": "local marker fixture only; no provider or remote-system evidence",
        }


def main() -> None:
    result = run()
    Path("durable-idempotency-sqlite-result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(result, indent=2, sort_keys=True))
    print("DURABLE SQLITE IDEMPOTENCY BOUNDARY: PASS")


if __name__ == "__main__":
    main()
