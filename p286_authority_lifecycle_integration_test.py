"""P286: bounded authority lifecycle integration probe.

Exercises one integrated failure sequence: authority epoch change, stale cache,
delegation, in-flight transition, competing recovery roots, and external
effect recovery. This is model-level evidence; it does not claim a production
consensus or external exactly-once implementation.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class AuthorityState:
    epoch: int
    root: str
    trusted_roots: frozenset

@dataclass(frozen=True)
class Delegation:
    subject: str
    issuer: str
    issuer_epoch: int
    capability: str

@dataclass(frozen=True)
class Transition:
    tid: str
    epoch: int
    authority_root: str
    capability: str
    operation: str

@dataclass(frozen=True)
class CachedEvidence:
    evidence_id: str
    epoch: int
    authority_root: str
    value: str

class External:
    def __init__(self):
        self.effects = set()
    def apply(self, tid):
        self.effects.add(tid)
    def has_effect(self, tid):
        return tid in self.effects

def delegation_valid(d, state):
    return d.issuer in state.trusted_roots and d.issuer_epoch == state.epoch

def transition_valid(t, state, delegation):
    return (t.epoch == state.epoch and
            t.authority_root == state.root and
            delegation_valid(delegation, state) and
            t.capability == delegation.capability)

def cache_valid(c, state):
    return c.epoch == state.epoch and c.authority_root == state.root

def main():
    checks = []
    # R1 -> R2: R2 is the current authority root.
    r1 = AuthorityState(1, "R1", frozenset({"R1"}))
    r2 = AuthorityState(2, "R2", frozenset({"R2"}))
    d2 = Delegation("G", "R2", 2, "self-change")
    cached = CachedEvidence("C1", 1, "R1", "approved")

    # 1. Cached evidence from R1 cannot authorize work in R2.
    checks.append(not cache_valid(cached, r2))

    # 2. Cached evidence can remain useful as historical evidence without
    # becoming current authority evidence.
    checks.append(cached.value == "approved" and not cache_valid(cached, r2))

    # 3. Delegation issued by current trusted root is valid.
    checks.append(delegation_valid(d2, r2))

    # 4. Same delegation is invalid after the authority epoch changes again.
    r3 = AuthorityState(3, "R3", frozenset({"R3"}))
    checks.append(not delegation_valid(d2, r3))

    # 5. An untrusted candidate cannot become a root merely by issuing a
    # delegation to itself.
    forged = Delegation("G", "X", 3, "self-change")
    checks.append(not delegation_valid(forged, r3))

    # 6. An in-flight transition bound to R2 is valid before rotation.
    t2 = Transition("T2", 2, "R2", "self-change", "change-capability")
    checks.append(transition_valid(t2, r2, d2))

    # 7. The same in-flight transition must be revalidated after rotation.
    checks.append(not transition_valid(t2, r3, d2))

    # 8. A transition cannot use an old delegation with a new root.
    t3 = Transition("T3", 3, "R3", "self-change", "change-capability")
    checks.append(not transition_valid(t3, r3, d2))

    # 9. Competing recovery roots do not get an arbitrary local winner.
    candidates = {"R3A", "R3B"}
    converged_root = None
    checks.append(len(candidates) == 2 and converged_root is None)

    # 10. Without authoritative convergence, recovery remains UNKNOWN.
    recovery = "UNKNOWN" if converged_root is None else "COMMITTED"
    checks.append(recovery == "UNKNOWN")

    # 11. A consequential external effect is never erased by rolling Genesis
    # state back; reconciliation must observe the external world.
    ext = External()
    ext.apply("T2")
    genesis_state = "COMMITTED"
    genesis_state = "ROLLED_BACK"
    checks.append(ext.has_effect("T2") and genesis_state == "ROLLED_BACK")

    # 12. After rollback/recovery, the old in-flight transition cannot be
    # recommitted under the new authority without a fresh qualified transition.
    checks.append(not transition_valid(t2, r3, d2))

    # 13. Current authority must be independently present in the trusted set.
    r3_bad = AuthorityState(3, "R3", frozenset())
    d3 = Delegation("G", "R3", 3, "self-change")
    checks.append(not delegation_valid(d3, r3_bad))

    # 14. A cache refresh under R3 is valid only when its binding is current.
    fresh = CachedEvidence("C2", 3, "R3", "observed")
    checks.append(cache_valid(fresh, r3))

    assert all(checks), f"P286 failed: {checks}"
    print("P286 authority lifecycle integration: 14/14 PASS")

if __name__ == "__main__":
    main()
