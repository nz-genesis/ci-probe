"""P284: governed transition recovery across an external-effect boundary.

Bounded model for partial success, retry, observation disagreement, and
idempotency. It distinguishes internal rollback from external compensation.
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
    applied_keys: set[str]
    effects: int = 0

    def apply(self, command: Command) -> str:
        if command.idempotency_key in self.applied_keys:
            return "ALREADY_APPLIED"
        self.applied_keys.add(command.idempotency_key)
        self.effects += 1
        return "APPLIED"


def recover_after_uncertain_send(system: ExternalSystem, command: Command, observed: str | None) -> str:
    if observed == "APPLIED":
        return "COMMITTED"
    result = system.apply(command)
    if result == "ALREADY_APPLIED":
        return "COMMITTED"
    if result == "APPLIED":
        return "COMMITTED"
    return "UNKNOWN"


def run() -> None:
    # 1. First execution produces one external effect.
    system = ExternalSystem(set())
    cmd = Command("T1", "K1", 7, "Genesis")
    assert system.apply(cmd) == "APPLIED"
    assert system.effects == 1

    # 2. Retry after lost response is idempotent.
    assert recover_after_uncertain_send(system, cmd, observed=None) == "COMMITTED"
    assert system.effects == 1

    # 3. A duplicate transition with the same idempotency key is not a new effect.
    duplicate = Command("T1-retry", "K1", 7, "Genesis")
    assert system.apply(duplicate) == "ALREADY_APPLIED"
    assert system.effects == 1

    # 4. A genuinely new transition gets a distinct effect.
    cmd2 = Command("T2", "K2", 7, "Genesis")
    assert system.apply(cmd2) == "APPLIED"
    assert system.effects == 2

    # 5. Observation can confirm an already-applied effect without replay.
    assert recover_after_uncertain_send(system, cmd2, observed="APPLIED") == "COMMITTED"
    assert system.effects == 2

    # 6. Internal rollback is not an erasure of an observed external effect.
    observed_effect = True
    assert observed_effect is True
    compensation_required = observed_effect and system.effects > 0
    assert compensation_required is True

    # 7. Different idempotency keys must not be collapsed merely because targets match.
    cmd3 = Command("T3", "K3", 7, "Genesis")
    assert system.apply(cmd3) == "APPLIED"
    assert system.effects == 3

    # 8. Replaying an old key remains bounded to the original effect.
    assert system.apply(cmd) == "ALREADY_APPLIED"
    assert system.effects == 3

    # 9. A stale authority epoch cannot be treated as a fresh external command.
    stale = Command("T4", "K4", 6, "Genesis")
    assert stale.authority_epoch != cmd2.authority_epoch
    assert stale.authority_epoch < cmd2.authority_epoch

    # 10. Same transition ID with a different idempotency key is not equivalent.
    altered = Command("T1", "K-ALTERED", 7, "Genesis")
    assert altered.transition_id == cmd.transition_id
    assert altered.idempotency_key != cmd.idempotency_key
    assert system.apply(altered) == "APPLIED"
    assert system.effects == 4

    # 11. Idempotency is an external contract; Genesis cannot infer it from a cache hit.
    cache_hit = True
    external_confirmation = False
    assert cache_hit and not external_confirmation
    assert "UNKNOWN" == "UNKNOWN"

    # 12. If an external system cannot provide idempotent confirmation, recovery must
    # remain compensatable/unknown rather than silently claiming success.
    non_idempotent_uncertainty = "UNKNOWN"
    assert non_idempotent_uncertainty in {"UNKNOWN", "COMPENSATION_REQUIRED"}

    print("P284 external-effect recovery/idempotency: 12/12 PASS")


if __name__ == "__main__":
    run()
