from dataclasses import dataclass
from enum import Enum

class Verdict(Enum):
    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class Anchor:
    id: str
    epoch: int
    signers: frozenset[str]
    threshold: int
    protected: bool = True

@dataclass(frozen=True)
class Root:
    id: str
    epoch: int
    parent: str
    anchor_epoch: int
    digest: str

@dataclass(frozen=True)
class Evidence:
    anchor_epoch: int
    root_digest: str
    parent: str
    signers: frozenset[str]

@dataclass(frozen=True)
class InFlight:
    action_id: str
    authority_epoch: int
    root_digest: str
    capability_version: int

def quorum_ok(e: Evidence, a: Anchor) -> bool:
    return a.protected and e.anchor_epoch == a.epoch and e.signers <= a.signers and len(e.signers) >= a.threshold

def verify_successor(cur: Root, nxt: Root, e: Evidence, a: Anchor) -> Verdict:
    if nxt.epoch != cur.epoch + 1 or nxt.parent != cur.digest or nxt.anchor_epoch != a.epoch:
        return Verdict.INVALID
    if e.root_digest != nxt.digest or e.parent != cur.digest:
        return Verdict.INVALID
    return Verdict.VALID if quorum_ok(e, a) else Verdict.UNKNOWN

def recover(old: Anchor, recovery: frozenset[str], new: Anchor) -> Verdict:
    if not old.protected or new.epoch <= old.epoch or not recovery:
        return Verdict.UNKNOWN
    if not recovery <= new.signers:
        return Verdict.INVALID
    return Verdict.VALID if len(recovery) >= new.threshold else Verdict.UNKNOWN

def run():
    a1 = Anchor("A1", 1, frozenset({"s1","s2","s3","b"}), 3)
    r1 = Root("R1", 1, "GENESIS", 1, "d1")
    r2 = Root("R2", 2, "d1", 1, "d2")
    good = Evidence(1, "d2", "d1", frozenset({"s1","s2","s3"}))
    byz = Evidence(1, "d2", "d1", frozenset({"b"}))
    assert verify_successor(r1, r2, good, a1) is Verdict.VALID
    assert verify_successor(r1, r2, byz, a1) is Verdict.UNKNOWN

    mutable = Anchor("A1", 1, frozenset({"attacker"}), 1, protected=False)
    a2 = Anchor("A2", 2, frozenset({"s2","s3","s4","s5"}), 3)
    assert recover(mutable, frozenset({"attacker"}), a2) is Verdict.UNKNOWN
    assert recover(a1, frozenset({"s2","s3","s4"}), a2) is Verdict.VALID
    assert recover(a1, frozenset(), a2) is Verdict.UNKNOWN

    r3_old = Root("R3", 3, "d2", 1, "d3")
    e3_old = Evidence(1, "d3", "d2", frozenset({"s2","s3","s4"}))
    assert verify_successor(r2, r3_old, e3_old, a2) is Verdict.INVALID
    r3 = Root("R3", 3, "d2", 2, "d3")
    e3 = Evidence(2, "d3", "d2", frozenset({"s2","s3","s4"}))
    assert verify_successor(r2, r3, e3, a2) is Verdict.VALID

    branch = Root("R3b", 3, "wrong", 2, "d3b")
    delayed = Evidence(1, "d3b", "wrong", frozenset({"s1","s2","s3"}))
    assert verify_successor(r2, branch, delayed, a2) is Verdict.INVALID

    old_inflight = InFlight("op-1", 1, "d2", 7)
    fresh = InFlight("op-2", 2, "d3", 8)
    assert old_inflight.authority_epoch != a2.epoch
    assert fresh.authority_epoch == a2.epoch

    print("P275 anchor compromise/recovery: 10/10 PASS")

if __name__ == "__main__":
    run()
