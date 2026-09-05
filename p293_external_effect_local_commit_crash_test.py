import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class Transition:
    transition_id: str
    epoch: int
    boundary: str
    expected_revision: int
    effect_key: str


def db():
    c = sqlite3.connect("file:p293?mode=memory&cache=shared", isolation_level=None)
    return c


def cas_commit(c, t):
    cur = c.execute(
        "UPDATE state SET revision=revision+1 WHERE id=1 AND epoch=? AND boundary=? AND revision=?",
        (t.epoch, t.boundary, t.expected_revision),
    )
    return cur.rowcount == 1


def external_effect(c, t):
    c.execute(
        "INSERT OR IGNORE INTO effects(key, transition_id, status) VALUES (?, ?, 'APPLIED')",
        (t.effect_key, t.transition_id),
    )
    return c.execute("SELECT transition_id,status FROM effects WHERE key=?", (t.effect_key,)).fetchone()


def receipt_matches(c, t):
    return c.execute(
        "SELECT 1 FROM effects WHERE key=? AND transition_id=? AND status='APPLIED'",
        (t.effect_key, t.transition_id),
    ).fetchone() == (1,)


def main():
    keeper = db()
    keeper.execute("CREATE TABLE state(id INTEGER PRIMARY KEY, epoch INTEGER, boundary TEXT, revision INTEGER)")
    keeper.execute("INSERT INTO state VALUES(1,7,'B1',41)")
    keeper.execute("CREATE TABLE effects(key TEXT PRIMARY KEY, transition_id TEXT, status TEXT)")
    c = db()

    t1 = Transition('T1', 7, 'B1', 41, 'K1')
    # 1. Normal effect then local commit.
    assert external_effect(c, t1) == ('T1', 'APPLIED')
    assert receipt_matches(c, t1)
    assert cas_commit(c, t1)

    # 2. Reconciliation after the local commit sees the same receipt and does not duplicate.
    assert external_effect(c, t1) == ('T1', 'APPLIED')
    assert c.execute("SELECT COUNT(*) FROM effects WHERE key='K1'").fetchone() == (1,)

    # Reset state for crash scenarios.
    keeper.execute("UPDATE state SET revision=41, epoch=7, boundary='B1' WHERE id=1")
    keeper.execute("DELETE FROM effects")

    t2 = Transition('T2', 7, 'B1', 41, 'K2')
    # 3. External effect occurs, then local process crashes before CAS.
    assert external_effect(c, t2) == ('T2', 'APPLIED')
    # 4. Recovery can establish effect existence but must not claim local commit yet.
    assert receipt_matches(c, t2)
    assert keeper.execute("SELECT revision FROM state WHERE id=1").fetchone() == (41,)

    # 5. If the authoritative state is still current, a receipt-bound recovery may safely
    # complete the local commit exactly once.
    assert cas_commit(c, t2)
    assert keeper.execute("SELECT revision FROM state WHERE id=1").fetchone() == (42,)
    assert not cas_commit(c, t2)

    # Reset for stale-state recovery.
    keeper.execute("UPDATE state SET revision=41, epoch=7, boundary='B1' WHERE id=1")
    keeper.execute("DELETE FROM effects")

    t3 = Transition('T3', 7, 'B1', 41, 'K3')
    assert external_effect(c, t3) == ('T3', 'APPLIED')
    # 6. A concurrent state transition makes T3 stale before recovery.
    keeper.execute("UPDATE state SET revision=42, epoch=8, boundary='B2' WHERE id=1")
    assert receipt_matches(c, t3)
    assert not cas_commit(c, t3)

    # 7. Stale receipt evidence cannot authorize a different current transition.
    t4 = Transition('T4', 8, 'B2', 42, 'K4')
    assert receipt_matches(c, t3)
    assert not receipt_matches(c, t4)
    assert cas_commit(c, t4)

    # 8. A receipt bound to another transition/key is not sufficient evidence for T4.
    assert external_effect(c, t3) == ('T3', 'APPLIED')
    assert not receipt_matches(c, t4)

    # 9. A new transition with a fresh key produces exactly one new external effect record.
    assert external_effect(c, t4) == ('T4', 'APPLIED')
    assert c.execute("SELECT COUNT(*) FROM effects").fetchone() == (3,)

    # 10. Final state and effect identities remain independently auditable.
    assert keeper.execute("SELECT epoch,boundary,revision FROM state WHERE id=1").fetchone() == (8, 'B2', 43)
    assert c.execute("SELECT transition_id FROM effects WHERE key='K4'").fetchone() == ('T4',)

    print("P293 external effect / local commit crash boundary: 10/10 PASS")


if __name__ == '__main__':
    main()
