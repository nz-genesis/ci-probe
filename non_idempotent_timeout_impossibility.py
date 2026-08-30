"""Bounded indistinguishability proof for non-idempotent timeout recovery.

After an external call times out, two worlds can be locally indistinguishable:
the effect may already have happened or may not have happened. Without an
independent query or idempotency guarantee, one recovery policy cannot be safe
in both worlds.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class World:
    effect_count: int


@dataclass(frozen=True)
class LocalTimeoutState:
    operation_id: str
    acknowledgement: bool


def recover(local: LocalTimeoutState, retry: bool, world: World) -> World:
    if retry:
        return World(world.effect_count + 1)
    return world


def main() -> None:
    # Same local state, two possible external histories.
    local = LocalTimeoutState("op-1", False)
    happened = World(1)
    not_happened = World(0)

    # If recovery retries, the already-affected world duplicates the effect.
    retry_happened = recover(local, True, happened)
    assert retry_happened.effect_count == 2

    # If recovery does not retry, the not-yet-affected world misses the effect.
    no_retry_not_happened = recover(local, False, not_happened)
    assert no_retry_not_happened.effect_count == 0

    # Local observations are identical in both worlds.
    assert local == LocalTimeoutState("op-1", False)

    # Therefore no policy based only on local timeout state can be safe in both
    # histories: retry duplicates one; no-retry loses the other.
    safe_retry = retry_happened.effect_count == 1 and no_retry_not_happened.effect_count == 1
    assert not safe_retry

    print("NON-IDEMPOTENT TIMEOUT IMPOSSIBILITY: 4/4 PASS")
    print("Invariant: without independent effect identity/query or idempotency, timeout recovery is observationally underdetermined")


if __name__ == "__main__":
    main()
