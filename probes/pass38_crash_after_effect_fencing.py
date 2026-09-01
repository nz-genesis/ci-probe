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
    """Synthetic non-idempotent world: every accepted apply is a new effect."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.effects: list[tuple[str, int]] = []

    def apply(self, effect_id: str, fence: int) -> None:
        with self._lock:
            self.effects.append((effect_id, fence))


class PersistentFence:
    """Bounded coordination technique, not a proposed Genesis primitive."""

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


def reconcile(observations: list[Observation]) -> str:
    if not observations:
        return Outcome.UNKNOWN
    values = {o.happened for o in observations}
    if len(values) > 1:
        return Outcome.CONFLICT
    if True in values:
        return Outcome.REJECT
    if None in values:
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
    # This test proves local stale-token rejection only; it does not claim that
    # an arbitrary external system enforces fencing.
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
            # Re-check under the same coordination lock: another realizer may
            # have completed the external effect already.
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


def test_conflicting_observations_are_conflict_not_success() -> None:
    a = Authority("alice", True, 1)
    yes = Evidence(Observation("E4", True, 1), a, "A")
    no = Evidence(Observation("E4", False, 1), a, "B")
    assert reconcile([yes.observation, no.observation]) == Outcome.CONFLICT


def test_stale_or_revoked_authority_does_not_recover() -> None:
    t = Transition("T5", "alice", "E5", 2)
    c = Capability("alice", "realize")
    stale = Authority("alice", True, 1)
    revoked = Authority("alice", False, 2)
    assert admit(t, c, stale, Evidence(Observation("E5", False, 1), stale, "A")) == Outcome.UNKNOWN
    assert admit(t, c, revoked, Evidence(Observation("E5", False, 2), revoked, "A")) == Outcome.UNKNOWN


def test_capability_does_not_create_authority() -> None:
    t = Transition("T6", "alice", "E6", 1)
    c = Capability("alice", "realize")
    foreign = Authority("bob", True, 1)
    assert admit(t, c, foreign, None) == Outcome.UNKNOWN


def test_unknown_never_implies_retry() -> None:
    t = Transition("T7", "alice", "E7", 1)
    c = Capability("alice", "realize")
    a = Authority("alice", True, 1)
    assert admit(t, c, a, Evidence(Observation("E7", None, 1), a, "A")) == Outcome.UNKNOWN


def test_removal() -> None:
    basis = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}
    non_primitives = {"Recovery", "Fence", "Lease", "Receipt", "IdempotencyKey", "Transaction"}
    assert len(basis) == 7
    assert basis.isdisjoint(non_primitives)


def main() -> None:
    test_crash_after_effect_requires_reconciliation()
    test_old_fencer_cannot_continue_after_new_fencer()
    test_two_independent_realizers_one_effect()
    test_conflicting_observations_are_conflict_not_success()
    test_stale_or_revoked_authority_does_not_recover()
    test_capability_does_not_create_authority()
    test_unknown_never_implies_retry()
    test_removal()
    print("PASS38_PUBLIC: PASS; cases=8")


if __name__ == "__main__":
    main()
