"""Pass 37: lost ACK, concurrent recovery, and non-idempotent effects.

Public-safe synthetic probe. No external service, private state, credentials,
corpus, or witness material is used. The probe tests semantic boundaries and
bounded implementation techniques; it does not define Genesis ontology.
"""

from dataclasses import dataclass
from enum import Enum
from threading import Barrier, Lock, Thread


class Outcome(str, Enum):
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
    """Synthetic non-idempotent world: every apply is a new external effect."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.count = 0
        self.effect_ids: list[str] = []

    def apply(self, effect_id: str) -> None:
        with self._lock:
            self.count += 1
            self.effect_ids.append(effect_id)


class LocalState:
    """Small recovery state; this is State/Transition composition, not a new primitive."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.realized_effects: set[str] = set()
        self.in_flight: set[str] = set()

    def reserve(self, effect_id: str) -> bool:
        with self._lock:
            if effect_id in self.realized_effects or effect_id in self.in_flight:
                return False
            self.in_flight.add(effect_id)
            return True

    def mark_realized(self, effect_id: str) -> None:
        with self._lock:
            self.in_flight.discard(effect_id)
            self.realized_effects.add(effect_id)

    def release_without_effect(self, effect_id: str) -> None:
        with self._lock:
            self.in_flight.discard(effect_id)

    def is_realized(self, effect_id: str) -> bool:
        with self._lock:
            return effect_id in self.realized_effects


def admit(
    transition: Transition,
    capability: Capability,
    authority: Authority,
    evidence: Evidence | None,
) -> Outcome:
    if capability.subject != transition.authority_subject:
        return Outcome.REJECT
    if capability.operation != "realize":
        return Outcome.REJECT
    if authority.subject != transition.authority_subject:
        return Outcome.UNKNOWN
    if not authority.active or authority.version != transition.constraint_version:
        return Outcome.UNKNOWN
    if evidence is None:
        # Missing knowledge about an external effect is not permission to repeat it.
        return Outcome.UNKNOWN
    if evidence.authority.subject != transition.authority_subject:
        return Outcome.UNKNOWN
    if evidence.authority.version != transition.constraint_version:
        return Outcome.UNKNOWN
    if evidence.observation.effect_id != transition.effect_id:
        return Outcome.UNKNOWN
    if evidence.observation.happened is True:
        return Outcome.REJECT
    if evidence.observation.happened is None:
        return Outcome.UNKNOWN
    return Outcome.ALLOW


def case_lost_ack_is_unknown_not_retry_permission() -> None:
    world = ExternalWorld()
    state = LocalState()
    transition = Transition("T1", "alice", "E1", 1)
    capability = Capability("alice", "realize")
    authority = Authority("alice", True, 1)

    assert state.reserve("E1")
    world.apply("E1")
    # Crash/lost ACK occurs before local state is updated.
    state.release_without_effect("E1")

    outcome = admit(transition, capability, authority, None)
    assert outcome is Outcome.UNKNOWN
    assert world.count == 1
    assert not state.is_realized("E1")


def case_positive_observation_closes_recovery_without_repeat() -> None:
    world = ExternalWorld()
    state = LocalState()
    transition = Transition("T2", "alice", "E2", 1)
    capability = Capability("alice", "realize")
    authority = Authority("alice", True, 1)

    state.reserve("E2")
    world.apply("E2")
    state.release_without_effect("E2")
    evidence = Evidence(Observation("E2", True, 1), authority, "observer-a")

    assert admit(transition, capability, authority, evidence) is Outcome.REJECT
    # Reconciliation records the observed external fact; it does not execute again.
    state.mark_realized("E2")
    assert state.is_realized("E2")
    assert world.count == 1


def case_explicit_negative_observation_allows_one_new_effect() -> None:
    world = ExternalWorld()
    state = LocalState()
    transition = Transition("T3", "alice", "E3", 1)
    capability = Capability("alice", "realize")
    authority = Authority("alice", True, 1)
    evidence = Evidence(Observation("E3", False, 1), authority, "observer-a")

    assert admit(transition, capability, authority, evidence) is Outcome.ALLOW
    assert state.reserve("E3")
    world.apply("E3")
    state.mark_realized("E3")
    assert world.count == 1
    assert state.is_realized("E3")


def case_concurrent_recovery_has_single_reservation() -> None:
    world = ExternalWorld()
    state = LocalState()
    transition = Transition("T4", "alice", "E4", 1)
    capability = Capability("alice", "realize")
    authority = Authority("alice", True, 1)
    evidence = Evidence(Observation("E4", False, 1), authority, "observer-a")
    barrier = Barrier(2)
    outcomes: list[Outcome] = []
    lock = Lock()

    def worker() -> None:
        barrier.wait()
        outcome = admit(transition, capability, authority, evidence)
        if outcome is Outcome.ALLOW and state.reserve("E4"):
            world.apply("E4")
            state.mark_realized("E4")
        else:
            outcome = Outcome.UNKNOWN
        with lock:
            outcomes.append(outcome)

    threads = [Thread(target=worker), Thread(target=worker)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert world.count == 1
    assert state.is_realized("E4")
    assert sorted(outcomes, key=lambda x: x.value).count(Outcome.ALLOW) == 1


def case_stale_evidence_blocks_reexecution() -> None:
    transition = Transition("T5", "alice", "E5", 2)
    capability = Capability("alice", "realize")
    authority = Authority("alice", True, 2)
    stale = Evidence(Observation("E5", False, 1), Authority("alice", True, 1), "observer-a")
    assert admit(transition, capability, authority, stale) is Outcome.UNKNOWN


def case_revoked_authority_blocks_recovery() -> None:
    transition = Transition("T6", "alice", "E6", 3)
    capability = Capability("alice", "realize")
    revoked = Authority("alice", False, 3)
    negative = Evidence(Observation("E6", False, 3), revoked, "observer-a")
    assert admit(transition, capability, revoked, negative) is Outcome.UNKNOWN


def case_capability_is_not_authority() -> None:
    transition = Transition("T7", "alice", "E7", 1)
    capability = Capability("alice", "realize")
    foreign_authority = Authority("bob", True, 1)
    assert admit(transition, capability, foreign_authority, None) is Outcome.UNKNOWN


def case_unknown_never_implies_unconditional_retry() -> None:
    transition = Transition("T8", "alice", "E8", 1)
    capability = Capability("alice", "realize")
    authority = Authority("alice", True, 1)
    unknown = Evidence(Observation("E8", None, 1), authority, "observer-a")
    assert admit(transition, capability, authority, unknown) is Outcome.UNKNOWN


def case_primitive_removal() -> None:
    # ACK, Retry, Recovery, IdempotencyKey, Receipt and Transaction are not
    # required as Genesis primitives by these vectors; they are techniques or
    # descriptive terms. The semantic test basis remains seven candidates.
    basis = {
        "State",
        "Transition",
        "Capability",
        "Authority",
        "Observation",
        "Evidence",
        "Constraint",
    }
    forbidden_additions = {"ACK", "Retry", "Recovery", "IdempotencyKey", "Receipt", "Transaction"}
    assert not (basis & forbidden_additions)
    assert len(basis) == 7


def main() -> None:
    case_lost_ack_is_unknown_not_retry_permission()
    case_positive_observation_closes_recovery_without_repeat()
    case_explicit_negative_observation_allows_one_new_effect()
    case_concurrent_recovery_has_single_reservation()
    case_stale_evidence_blocks_reexecution()
    case_revoked_authority_blocks_recovery()
    case_capability_is_not_authority()
    case_unknown_never_implies_unconditional_retry()
    case_primitive_removal()
    print("PASS37_PUBLIC: PASS; cases=9")


if __name__ == "__main__":
    main()
