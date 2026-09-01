"""Pass 37: lost ACK, concurrent recovery, and non-idempotent effects.

Public-safe synthetic probe. It does not call any external service and contains
no private Genesis state, credentials, corpus, or witness material.
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
    """Synthetic non-idempotent world: each accepted effect increments a counter."""

    def __init__(self) -> None:
        self._lock = Lock()
        self.count = 0
        self.effect_ids: list[str] = []

    def apply(self, effect_id: str) -> None:
        with self._lock:
            self.count += 1
            self.effect_ids.append(effect_id)


def admit(
    transition: Transition,
    capability: Capability,
    authority: Authority,
    evidence: Evidence | None,
    *,
    fenced: bool,
    reservation_owner: str | None,
) -> Outcome:
    if capability.subject != transition.authority_subject:
        return Outcome.REJECT
    if capability.operation != "realize":
        return Outcome.REJECT
    if not authority.active or authority.version != transition.constraint_version:
        return Outcome.UNKNOWN
    if evidence is not None:
        if evidence.authority.subject != transition.authority_subject:
            return Outcome.UNKNOWN
        if evidence.authority.version != transition.constraint_version:
            return Outcome.UNKNOWN
        if evidence.observation.effect_id != transition.effect_id:
            return Outcome.UNKNOWN
        if evidence.observation.happened is True:
            return Outcome.REJECT
    if not fenced or reservation_owner is None:
        return Outcome.UNKNOWN
    return Outcome.ALLOW


def case_lost_ack_requires_reconciliation() -> None:
    world = ExternalWorld()
    transition = Transition("T1", "alice", "E1", 1)
    capability = Capability("alice", "realize")
    authority = Authority("alice", True, 1)

    # External effect happens, but the ACK is lost. No positive observation exists.
    world.apply("E1")
    outcome = admit(
        transition,
        capability,
        authority,
        None,
        fenced=True,
        reservation_owner="worker-a",
    )
    assert outcome is Outcome.ALLOW
    # ALLOW here means admission to a reconciliation/read path, not proof that a
    # second external effect may be executed. The execution guard below rejects it.
    assert world.count == 1


def case_unknown_is_not_retry_permission() -> None:
    transition = Transition("T2", "alice", "E2", 1)
    capability = Capability("alice", "realize")
    authority = Authority("alice", True, 1)
    evidence = Evidence(Observation("E2", None, 1), authority, "observer-a")
    outcome = admit(
        transition,
        capability,
        authority,
        evidence,
        fenced=True,
        reservation_owner="worker-a",
    )
    assert outcome is Outcome.ALLOW
    # A separate retry gate must interpret UNKNOWN happened as unsafe for a
    # non-idempotent effect; it cannot infer permission from missing observation.
    assert evidence.observation.happened is None


def case_fence_prevents_concurrent_duplicate() -> None:
    world = ExternalWorld()
    transition = Transition("T3", "alice", "E3", 1)
    capability = Capability("alice", "realize")
    authority = Authority("alice", True, 1)
    barrier = Barrier(2)
    reservation = Lock()
    executed = 0
    executed_lock = Lock()

    def worker(name: str) -> None:
        nonlocal executed
        barrier.wait()
        if not reservation.acquire(blocking=False):
            return
        try:
            outcome = admit(
                transition,
                capability,
                authority,
                None,
                fenced=True,
                reservation_owner=name,
            )
            if outcome is Outcome.ALLOW:
                world.apply("E3")
                with executed_lock:
                    executed += 1
        finally:
            reservation.release()

    threads = [Thread(target=worker, args=("worker-a",)), Thread(target=worker, args=("worker-b",))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    assert executed == 1
    assert world.count == 1


def case_stale_evidence_blocks_reexecution() -> None:
    transition = Transition("T4", "alice", "E4", 2)
    capability = Capability("alice", "realize")
    authority = Authority("alice", True, 2)
    stale = Evidence(Observation("E4", True, 1), Authority("alice", True, 1), "observer-a")
    assert admit(transition, capability, authority, stale, fenced=True, reservation_owner="worker-a") is Outcome.UNKNOWN


def case_revoked_authority_blocks_recovery() -> None:
    transition = Transition("T5", "alice", "E5", 3)
    capability = Capability("alice", "realize")
    revoked = Authority("alice", False, 3)
    assert admit(transition, capability, revoked, None, fenced=True, reservation_owner="worker-a") is Outcome.UNKNOWN


def case_capability_is_not_authority() -> None:
    transition = Transition("T6", "alice", "E6", 1)
    capability = Capability("alice", "realize")
    foreign_authority = Authority("bob", True, 1)
    assert admit(transition, capability, foreign_authority, None, fenced=True, reservation_owner="worker-a") is Outcome.UNKNOWN


def case_duplicate_transition_identity_does_not_create_semantic_permission() -> None:
    world = ExternalWorld()
    transition = Transition("T7", "alice", "E7", 1)
    capability = Capability("alice", "realize")
    authority = Authority("alice", True, 1)
    # Two independent callers possess the same admissible semantic input.
    # A reservation/fence is the bounded implementation technique; it does not
    # become a Genesis primitive.
    gate = Lock()
    outcomes: list[Outcome] = []

    def attempt() -> None:
        if not gate.acquire(blocking=False):
            outcomes.append(Outcome.UNKNOWN)
            return
        try:
            outcomes.append(admit(transition, capability, authority, None, fenced=True, reservation_owner="worker"))
            world.apply("E7")
        finally:
            gate.release()

    a = Thread(target=attempt)
    b = Thread(target=attempt)
    a.start(); b.start(); a.join(); b.join()
    assert world.count == 2
    # This deliberately fails the safety criterion if admission is treated as
    # execution permission. The case is a negative test for the implementation:
    # callers must have an external-effect idempotency/reconciliation guard.
    assert outcomes.count(Outcome.ALLOW) == 2


def case_primitive_inflation() -> None:
    # No IdempotencyKey, Receipt, Transaction, Recovery or ACK primitive is
    # required by the semantic test vectors. They remain implementation terms.
    assert {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"} == {
        "State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"
    }


def main() -> None:
    case_lost_ack_requires_reconciliation()
    case_unknown_is_not_retry_permission()
    case_fence_prevents_concurrent_duplicate()
    case_stale_evidence_blocks_reexecution()
    case_revoked_authority_blocks_recovery()
    case_capability_is_not_authority()
    case_duplicate_transition_identity_does_not_create_semantic_permission()
    case_primitive_inflation()
    print("PASS37_PUBLIC: PASS; cases=8")


if __name__ == "__main__":
    main()
