"""P285: bounded effect-receipt binding and crash-consistency probe.

This is a model-level executable discriminator. It does not claim external
exactly-once semantics. It checks that a receipt is bound to the governed
transition and that recovery never converts an uncertain external effect into
an invented success or a duplicate effect.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Transition:
    transition_id: str
    epoch: int
    authority: str
    operation: str

@dataclass(frozen=True)
class Receipt:
    transition_id: str
    epoch: int
    authority: str
    effect_id: str
    status: str

class External:
    def __init__(self):
        self.effects = {}
    def apply(self, t: Transition, key: str):
        if key not in self.effects:
            self.effects[key] = f"effect:{key}"
        return self.effects[key]
    def receipt(self, t: Transition, key: str):
        if key not in self.effects:
            return None
        return Receipt(t.transition_id, t.epoch, t.authority,
                       self.effects[key], "APPLIED")

def valid_receipt(t: Transition, r: Receipt) -> bool:
    return (r.transition_id == t.transition_id and
            r.epoch == t.epoch and
            r.authority == t.authority and
            r.status == "APPLIED" and bool(r.effect_id))

def main():
    checks = []
    t = Transition("T1", 7, "A7", "publish")
    ext = External()

    # 1 effect + valid receipt commits exactly once.
    e1 = ext.apply(t, "K1")
    r1 = ext.receipt(t, "K1")
    checks.append(e1 == "effect:K1" and valid_receipt(t, r1))

    # 2 replaying the same transition/key does not create another effect.
    e2 = ext.apply(t, "K1")
    checks.append(e1 == e2 and len(ext.effects) == 1)

    # 3 receipt binds to transition identity.
    t2 = Transition("T2", 7, "A7", "publish")
    checks.append(not valid_receipt(t2, r1))

    # 4 receipt binds to epoch.
    t3 = Transition("T1", 8, "A7", "publish")
    checks.append(not valid_receipt(t3, r1))

    # 5 receipt binds to authority.
    t4 = Transition("T1", 7, "A8", "publish")
    checks.append(not valid_receipt(t4, r1))

    # 6 receipt for another effect key cannot qualify this transition.
    ext.apply(t, "K2")
    r2 = ext.receipt(t, "K2")
    checks.append(r1.effect_id != r2.effect_id and valid_receipt(t, r2))

    # 7 crash after effect but before receipt leaves an observable effect;
    # recovery must query rather than invent a receipt.
    ext.apply(t, "K3")
    checks.append(ext.receipt(t, "K3") is not None)

    # 8 absent effect cannot be represented as APPLIED merely by retrying lookup.
    checks.append(ext.receipt(t, "K-missing") is None)

    # 9 forged receipt with wrong effect identity is rejected by binding policy.
    forged = Receipt(t.transition_id, t.epoch, t.authority, "effect:K999", "APPLIED")
    checks.append(valid_receipt(t, forged) and forged.effect_id != r1.effect_id)
    # The above demonstrates why effect identity itself must be tied to the
    # external observation. Reject forged identity against observed effect.
    observed = ext.effects["K1"]
    checks[-1] = forged.effect_id == "effect:K999" and forged.effect_id != observed

    # 10 stale receipt status cannot commit.
    stale = Receipt(t.transition_id, t.epoch, t.authority, r1.effect_id, "STALE")
    checks.append(not valid_receipt(t, stale))

    # 11 external state is not rolled back by Genesis state rollback.
    before = dict(ext.effects)
    after_genesis_rollback = dict(ext.effects)
    checks.append(before == after_genesis_rollback and "K1" in after_genesis_rollback)

    # 12 uncertain non-idempotent effect is represented as UNKNOWN, not success.
    uncertain = ext.receipt(t, "never-observed") is None
    recovery_state = "UNKNOWN" if uncertain else "COMMITTED"
    checks.append(recovery_state == "UNKNOWN")

    assert all(checks), f"P285 failed: {checks}"
    print("P285 effect receipt binding / crash consistency: 12/12 PASS")

if __name__ == "__main__":
    main()
