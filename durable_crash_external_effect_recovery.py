"""Bounded durable-crash recovery probe for external effects."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Provider:
    idempotent: bool
    effect_count: int = 0

def execute(provider: Provider, crash_after_effect: bool) -> tuple[Provider, bool]:
    p = Provider(provider.idempotent, provider.effect_count + 1)
    return p, not crash_after_effect

def retry(provider: Provider) -> Provider:
    if provider.idempotent:
        return provider
    return Provider(provider.idempotent, provider.effect_count + 1)

def recover(local_ack: bool, observed_effect: bool | None) -> str:
    if observed_effect is True:
        return "CONFIRMED"
    if observed_effect is False:
        return "ABSENT"
    if local_ack:
        return "ACKNOWLEDGED"
    return "UNKNOWN"

def main() -> None:
    p, ack = execute(Provider(False), False)
    assert recover(ack, None) == "ACKNOWLEDGED"

    p, ack = execute(Provider(False), True)
    assert recover(ack, None) == "UNKNOWN"
    assert recover(ack, True) == "CONFIRMED"

    idem, ack = execute(Provider(True), True)
    before = idem.effect_count
    assert retry(idem).effect_count == before
    assert not ack

    non, ack = execute(Provider(False), True)
    before = non.effect_count
    assert retry(non).effect_count == before + 1

    assert recover(True, False) == "ABSENT"
    print("DURABLE CRASH EXTERNAL EFFECT RECOVERY: 6/6 PASS")

if __name__ == "__main__":
    main()
