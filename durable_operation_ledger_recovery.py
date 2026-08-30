"""Bounded crash/restart operation-ledger recovery probe.

Discriminator: durable intent/effect identity survives process restart, while
world-state confirmation remains separate from local ledger state.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Record:
    op_id: str
    phase: str
    effect_id: str | None = None


def recover(record: Record, observed_effect_id: str | None) -> str:
    if observed_effect_id == record.effect_id and observed_effect_id is not None:
        return "CONFIRMED"
    if record.phase == "PREPARED":
        return "READY_TO_EXECUTE"
    if record.phase == "EFFECT_ATTEMPTED":
        return "UNKNOWN"
    if record.phase == "CONFIRMED":
        return "CONFIRMED"
    return "INVALID"


def main() -> None:
    # 1. Prepared intent survives restart and can be executed once.
    prepared = Record("op-1", "PREPARED")
    assert recover(prepared, None) == "READY_TO_EXECUTE"

    # 2. Crash after effect identity is durable but before confirmation.
    attempted = Record("op-2", "EFFECT_ATTEMPTED", "effect-2")
    assert recover(attempted, None) == "UNKNOWN"

    # 3. Independent observation closes the attempted operation.
    assert recover(attempted, "effect-2") == "CONFIRMED"

    # 4. Wrong observation must not close the operation.
    assert recover(attempted, "effect-other") == "UNKNOWN"

    # 5. A durable CONFIRMED record is reconstructible after restart.
    confirmed = Record("op-3", "CONFIRMED", "effect-3")
    assert recover(confirmed, "effect-3") == "CONFIRMED"

    # 6. Operation identity alone is not world-state evidence.
    assert recover(Record("op-4", "EFFECT_ATTEMPTED", "effect-4"), None) == "UNKNOWN"

    print("DURABLE OPERATION LEDGER RECOVERY: 6/6 PASS")

if __name__ == "__main__":
    main()
