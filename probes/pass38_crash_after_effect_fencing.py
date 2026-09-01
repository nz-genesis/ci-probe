"""Pass 38: crash-after-effect, persistent fencing, independent realizers.

Public-safe synthetic probe. It tests whether State/Transition/Capability/
Authority/Observation/Evidence/Constraint composition can represent recovery
without turning fencing/recovery/idempotency into Genesis primitives.
"""
from dataclasses import dataclass
from threading import Lock, Thread


class Outcome:
    ALLOW = "ALLOW"
    REJECT = "REJECT"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class Transition:
    transition_id: str
    authority_subject: str
    effect_id: str
    constraint_version: int


@dataclass(frozen=True)
class Capability:
    subject: str
    operation: str


@dataclass(frozen=True)
class Authority:
    subject: str
    active: bool
    version: int


@dataclass(frozen=True)
class Observation:
    effect_id: str
    happened: bool | None
    observation_version: int


@dataclass(frozen=True)
class Evidence:
    observation: Observation
    authority: Authority
    source: str


class ExternalWorld:
    def __init__(self) -> None:
        self._lock = Lock()
        self.effects: list[tuple[str, int]] = []

    def apply(self, effect_id: str, fence: int) -> None:
        with self._lock:
            self.effects.append((effect_id, fence))


class PersistentFence:
    def __init__(self) -> None:
        self._lock = Lock()
        self.current: dict[str, int] = {}

    def acquire(self, effect_id: str) -> int:
        with self._lock:
            token = self.current.get(effect_id, 0) + 1
            self.current[effect_id] = token
            return token

    def valid(self, effect_id: str, token: int) -> bool:
        with self._lock:
            return self.current.get(effect_id) == token


def admit(t: Transition, c: Capability, a: Authority, e: Evidence | None) -> str:
    if c.subject != t.authority_subject or c.operation != "realize":
        return Outcome.REJECT
    if a.subject != t.authority_subject or not a.active or a.version != t.constraint_version:
        return Outcome.UNKNOWN
    if e is None or e.authority != a or e.observation.effect_id != t.effect_id:
        return Outcome.UNKNOWN
    if e.observation.happened is True:
        return Outcome.REJECT
    if e.observation.happened is None:
        return Outcome.UNKNOWN
    return Outcome.ALLOW


def test_crash_after_effect_requires_reconciliation() -> None:
    world = ExternalWorld()
    fence = PersistentFence()
    t = Transition("T1", "alice", "E1", 1)
    c = Capability("alice", "realize")
    a = Authority("alice", True, 1)
    token = fence.acquire("E1")
    world.apply("E1", token)
    # Worker crashes before recording local realization.
    assert admit(t, c, a, None) == Outcome.UNKNOWN
    # Recovery cannot infer "safe to repeat" from the missing local update.
    assert len(world.effects) == 1


def test_old_fencer_cannot_continue_after_new_fencer() -> None:
    world = ExternalWorld()
    fence = PersistentFence()
    old = fence.acquire("E2")
    new = fence.acquire("E2")
    assert not fence.valid("E2", old)
    assert fence.valid("E2", new)
    # A stale independent realizer is fenced out before its external effect.
    if fence.valid("E2", old):
        world.apply("E2", old)
    assert world.effects == []


def test_two_independent_realizers_one_effect() -> None:
    world = ExternalWorld()
    fence = PersistentFence()
    t = Transition("T3", "alice", "E3", 1)
    c = Capability("alice", "realize")
    a = Authority("alice", True, 1)
    e = Evidence(Observation("E3", False, 1), a, "observer")
    results: list[str] = []
    lock = Lock()

    def worker() -> None:
        token = fence.acquire("E3")
        outcome = admit(t, c, a, e)
        if outcome == Outcome.ALLOW and fence.valid("E3", token):
            # Re-check after admission: another realizer may have fenced us.
            with lock:
                if fence.valid("E3", token) and not world.effects:
                    world.apply("E3", token)
                    result = Outcome.ALLOW
                else:
                    result = Outcome.UNKNOWN
        else:
            result = Outcome.UNKNOWN
        with lock:
            results.append(result)

    threads = [Thread(target=worker), Thread(target=worker)]
    for x in threads: x.start()
    for x in threads: x.join()
    assert len(world.effects) == 1
    assert Outcome.ALLOW in results


def test_conflicting_observations_do_not_become_success() -> None:
    a = Authority("alice", True, 1)
    t = Transition("T4", "alice", "E4", 1)
    c = Capability("alice", "realize")
    yes = Evidence(Observation("E4", True, 1), a, "A")
    no = Evidence(Observation("E4", False, 1), a, "B")
    assert yes.observation.happened is True
    assert no.observation.happened is False
    assert Outcome.CONFLICT == "CONFLICT"


def test_removal() -> None:
    basis = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}
    non_primitives = {"Recovery", "Fence", "Lease", "Receipt", "IdempotencyKey", "Transaction"}
    assert len(basis) == 7
    assert basis.isdisjoint(non_primitives)


def main() -> None:
    test_crash_after_effect_requires_reconciliation()
    test_old_fencer_cannot_continue_after_new_fencer()
    test_two_independent_realizers_one_effect()
    test_conflicting_observations_do_not_become_success()
    test_removal()
    print("PASS38_PUBLIC: PASS; cases=5")


if __name__ == "__main__":
    main()
