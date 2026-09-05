import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Transition:
    epoch: int
    boundary_version: str
    expected_revision: int
    transition_id: str


def connect(db):
    return sqlite3.connect(db, isolation_level=None)


def init(db):
    c = connect(db)
    c.execute("CREATE TABLE state (id INTEGER PRIMARY KEY, epoch INTEGER, boundary TEXT, revision INTEGER)")
    c.execute("INSERT INTO state VALUES (1, 7, 'B1', 41)")
    c.execute("CREATE TABLE effects (key TEXT PRIMARY KEY, transition_id TEXT, status TEXT)")
    c.close()


def cas_commit(c, t: Transition):
    cur = c.execute(
        "UPDATE state SET revision = revision + 1, epoch = ?, boundary = ? "
        "WHERE id = 1 AND epoch = ? AND boundary = ? AND revision = ?",
        (t.epoch, t.boundary_version, t.epoch, t.boundary_version, t.expected_revision),
    )
    return cur.rowcount == 1


def record_receipt(c, key, transition_id):
    c.execute("INSERT OR IGNORE INTO effects VALUES (?, ?, 'APPLIED')", (key, transition_id))
    row = c.execute("SELECT transition_id, status FROM effects WHERE key = ?", (key,)).fetchone()
    return row


def main():
    db = ':memory:'
    # SQLite in-memory databases are connection-local; use a shared URI for the concrete runtime test.
    db = 'file:p292?mode=memory&cache=shared'
    keeper = connect(db)
    keeper.execute("CREATE TABLE state (id INTEGER PRIMARY KEY, epoch INTEGER, boundary TEXT, revision INTEGER)")
    keeper.execute("INSERT INTO state VALUES (1, 7, 'B1', 41)")
    keeper.execute("CREATE TABLE effects (key TEXT PRIMARY KEY, transition_id TEXT, status TEXT)")

    a = connect(db)
    b = connect(db)

    # 1. Both readers observe the same revision.
    snapshot_a = a.execute("SELECT epoch, boundary, revision FROM state WHERE id=1").fetchone()
    snapshot_b = b.execute("SELECT epoch, boundary, revision FROM state WHERE id=1").fetchone()
    assert snapshot_a == snapshot_b == (7, 'B1', 41)

    t_a = Transition(7, 'B1', 41, 'T-A')
    t_b = Transition(7, 'B1', 41, 'T-B')

    # 2. First compare-and-commit wins.
    assert cas_commit(a, t_a)

    # 3. Second writer with the stale revision loses.
    assert not cas_commit(b, t_b)

    # 4. Current state is exactly one revision ahead.
    assert keeper.execute("SELECT epoch, boundary, revision FROM state WHERE id=1").fetchone() == (7, 'B1', 42)

    # 5. A fresh transition can commit against the current revision.
    t_c = Transition(7, 'B1', 42, 'T-C')
    assert cas_commit(b, t_c)

    # 6. Crash after external effect but before local receipt persistence is represented
    # by an effect that can be observed by its idempotency key.
    record_receipt(keeper, 'K-C', 'T-C')
    assert keeper.execute("SELECT status FROM effects WHERE key='K-C'").fetchone() == ('APPLIED',)

    # 7. Reconciliation finds the already-applied effect; it must not create another row.
    assert record_receipt(keeper, 'K-C', 'T-C') == ('T-C', 'APPLIED')
    assert keeper.execute("SELECT COUNT(*) FROM effects WHERE key='K-C'").fetchone() == (1,)

    # 8. A receipt for another transition cannot be bound to T-C.
    record_receipt(keeper, 'K-X', 'T-X')
    assert keeper.execute("SELECT transition_id FROM effects WHERE key='K-X'").fetchone() == ('T-X',)
    assert keeper.execute("SELECT transition_id FROM effects WHERE key='K-X'").fetchone()[0] != t_c.transition_id

    # 9. Stale T-A remains rejected even after reconciliation.
    assert not cas_commit(a, t_a)

    # 10. Current state demonstrates monotonic revision after successful CAS commits.
    assert keeper.execute("SELECT revision FROM state WHERE id=1").fetchone() == (43,)

    a.close(); b.close(); keeper.close()
    print("P292 runtime compare-and-commit / receipt composition: 10/10 PASS")


if __name__ == '__main__':
    main()
