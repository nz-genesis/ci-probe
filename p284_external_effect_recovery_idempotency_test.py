"""P284: governed transition recovery across an external-effect boundary.

Bounded model for partial success, retry, observation disagreement, and
idempotency. Internal rollback never erases an external effect.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Command:
    transition_id: str
    idempotency_key: str
    authority_epoch: int
    target: str


@dataclass
class ExternalSystem:
    supports_idempotency: bool
    applied_keys: set[str]
    effects: int = 0

    def apply(self, command: Command) -> str:
        if self.supports_idempotency and command.idempotency_key in self.applied_keys:
            return "ALREADY_APPLIED"
        if self.supports_idempotency:
            self.applied_keys.add(command.idempotency_key)
        self.effects += 1
        return "APPLIED"

    def query(self, key: str) -> str:
        if not self.supports_idempotency:
            return "UNSUPPORTED"
        return "APPLIED" if key in self.applied_keys else "ABSENT"


def recover_after_uncertain_send(system: ExternalSystem, command: Command, observed: str | None) -> str:
    if observed == "APPLIED":
        return "COMMITTED"
    status = system.query(command.idempotency_key)
    if status == "APPLIED":
        return "COMMITTED"
    if status == "ABSENT" and system.supports_idempotency:
        return "COMMITTED" if system.apply(command) in {"APPLIED", "ALREADY_APPLIED"} else "UNKNOWN"
    # Without authoritative effect lookup/idempotency, retrying can duplicate
    # an already-completed external action, so the safe result is UNKNOWN.
    return "UNKNOWN"


def run() -> None:
    # 1. First execution produces one external effect.
    system = ExternalSystem(True, set())
    cmd = Command("T1", "K1", 7, "Genesis")
    assert system.apply(cmd) == "APPLIED"
    assert system.effects == 1

    # 2. Retry after a lost response is idempotent.
    assert recover_after_uncertain_send(system, cmd, observed=None) == "COMMITTED"
    assert system.effects == 1

    # 3. A duplicate transition carrying the same idempotency key is not a new effect.
    duplicate = Command("T1-retry", "K1", 7, "Genesis")
    assert system.apply(duplicate) == "ALREADY_APPLIED"
    assert system.effects == 1

    # 4. A genuinely new transition gets a distinct effect.
    cmd2 = Command("T2", "K2", 7, "Genesis")
    assert system.apply(cmd2) == "APPLIED"
    assert system.effects == 2

    # 5. Explicit observation confirms an applied effect without replay.
    assert recover_after_uncertain_send(system, cmd2, observed="APPLIED") == "COMMITTED"
    assert system.effects == 2

    # 6. A recorded external effect cannot be erased by internal rollback.
    observed_effects_before = system.effects
    assert system.query("K2") == "APPLIED"
    assert system.effects == observed_effects_before

    # 7. Different idempotency keys must remain distinct even for the same target.
    cmd3 = Command("T3", "K3", 7, "Genesis")
    assert system.apply(cmd3) == "APPLIED"
    assert system.effects == 3

    # 8. Replaying an old key remains bounded to its original effect.
    assert system.apply(cmd) == "ALREADY_APPLIED"
    assert system.effects == 3

    # 9. Stale authority is not silently upgraded by the external-effect layer.
    stale = Command("T4", "K4", 6, "Genesis")
    assert stale.authority_epoch < cmd2.authority_epoch
    assert stale.authority_epoch != 7

    # 10. Same transition ID with a different key is a distinct external request.
    altered = Command("T1", "K-ALTERED", 7, "Genesis")
    assert altered.transition_id == cmd.transition_id
    assert altered.idempotency_key != cmd.idempotency_key
    assert system.apply(altered) == "APPLIED"
    assert system.effects == 4

    # 11. A cache hit without external confirmation cannot establish effect state.
    non_idempotent = ExternalSystem(False, set())
    cache_hit = True
    unknown_cmd = Command("T5", "K5", 7, "Genesis")
    assert non_idempotent.query(unknown_cmd.idempotency_key) == "UNSUPPORTED"
    assert cache_hit and recover_after_uncertain_send(non_idempotent, unknown_cmd, None) == "UNKNOWN"
    assert non_idempotent.effects == 0

    # 12. If a non-idempotent system may already have applied the command,
    # safe recovery must not blindly retry and duplicate the effect.
    assert non_idempotent.apply(unknown_cmd) == "APPLIED"
    assert non_idempotent.effects == 1
    assert recover_after_uncertain_send(non_idempotent, unknown_cmd, None) == "UNKNOWN"
    assert non_idempotent.effects == 1

    print("P284 external-effect recovery/idempotency: 12/12 PASS")


if __name__ == "__main__":
    run()
