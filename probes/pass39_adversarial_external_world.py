"""Pass 39: adversarial external world ignores local fencing.

Public-safe synthetic probe. The external realization deliberately accepts every
request, including stale fence tokens. The purpose is to separate Genesis
semantic uncertainty from guarantees that belong to a realization substrate.
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
    subject: str
    effect_id: str
    authority_version: int


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
    version: int


@dataclass(frozen=True)
class Evidence:
    observation: Observation
    authority: Authority
    source: str


class AdversarialExternalWorld:
    """Intentionally ignores fencing and accepts every apply as a new effect."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.effects: list[tuple[str, int, str]] = []

    def apply(self, effect_id: str, fence: int, realizer: str) -> None:
        with self._lock:
            self.effects.append((effect_id, fence, realizer))


class LocalFence:
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
    if c.subject != t.subject or c.operation != "realize":
        return Outcome.REJECT
    if a.subject != t.subject or not a.active or a.version != t.authority_version:
        return Outcome.UNKNOWN
    if e is None:
        return Outcome.UNKNOWN
    if e.authority != a or e.observation.effect_id != t.effect_id:
        return Outcome.UNKNOWN
    if e.observation.version != t.authority_version:
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


def test_local_fence_cannot_claim_external_safety() -> None:
    world = AdversarialExternalWorld()
    fence = LocalFence()
    old = fence.acquire("E1")
    new = fence.acquire("E1")
    assert not fence.valid("E1", old)
    assert fence.valid("E1", new)

    # Deliberately bypass the local validity check: the external world accepts
    # stale tokens. This is a substrate property, not Genesis authorization.
    world.apply("E1", old, "stale-worker")
    world.apply("E1", new, "new-worker")
    assert len(world.effects) == 2


def test_genesis_does_not_turn_unknown_into_retry() -> None:
    t = Transition("T2", "alice", "E2", 1)
    c = Capability("alice", "realize")
    a = Authority("alice", True, 1)
    unknown = Evidence(Observation("E2", None, 1), a, "observer")
    assert admit(t, c, a, unknown) == Outcome.UNKNOWN


def test_positive_observation_prevents_new_admission() -> None:
    t = Transition("T3", "alice", "E3", 1)
    c = Capability("alice", "realize")
    a = Authority("alice", True, 1)
    happened = Evidence(Observation("E3", True, 1), a, "observer")
    assert admit(t, c, a, happened) == Outcome.REJECT


def test_negative_observation_is_bounded_permission() -> None:
    t = Transition("T4", "alice", "E4", 1)
    c = Capability("alice", "realize")
    a = Authority("alice", True, 1)
    not_happened = Evidence(Observation("E4", False, 1), a, "observer")
    assert admit(t, c, a, not_happened) == Outcome.ALLOW


def test_conflicting_observations_are_conflict() -> None:
    a = Authority("alice", True, 1)
    yes = Evidence(Observation("E5", True, 1), a, "A")
    no = Evidence(Observation("E5", False, 1), a, "B")
    assert reconcile([yes.observation, no.observation]) == Outcome.CONFLICT


def test_two_realizers_demonstrate_external_non_idempotence() -> None:
    world = AdversarialExternalWorld()
    fence = LocalFence()
    t = Transition("T6", "alice", "E6", 1)
    c = Capability("alice", "realize")
    a = Authority("alice", True, 1)
    e = Evidence(Observation("E6", False, 1), a, "observer")
    start = fence.acquire("E6")
    second = fence.acquire("E6")
    assert admit(t, c, a, e) == Outcome.ALLOW
    results: list[str] = []
    lock = Lock()

    def worker(token: int, name: str) -> None:
        # Both realizers are assumed to reach the external world. The substrate
        # ignores fencing, so local fencing cannot prevent two external effects.
        world.apply("E6", token, name)
        with lock:
            results.append(Outcome.ALLOW)

    threads = [Thread(target=worker, args=(start, "A")), Thread(target=worker, args=(second, "B"))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert len(results) == 2
    assert len(world.effects) == 2


def test_capability_never_creates_authority() -> None:
    t = Transition("T7", "alice", "E7", 1)
    c = Capability("alice", "realize")
    foreign = Authority("bob", True, 1)
    assert admit(t, c, foreign, None) == Outcome.UNKNOWN


def test_primitive_removal() -> None:
    basis = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}
    realization_techniques = {"Fence", "Lease", "Retry", "Receipt", "IdempotencyKey", "Transaction", "Recovery"}
    assert len(basis) == 7
    assert basis.isdisjoint(realization_techniques)


def main() -> None:
    test_local_fence_cannot_claim_external_safety()
    test_genesis_does_not_turn_unknown_into_retry()
    test_positive_observation_prevents_new_admission()
    test_negative_observation_is_bounded_permission()
    test_conflicting_observations_are_conflict()
    test_two_realizers_demonstrate_external_non_idempotence()
    test_capability_never_creates_authority()
    test_primitive_removal()
    print("PASS39_PUBLIC: PASS; cases=8")


if __name__ == "__main__":
    main()
