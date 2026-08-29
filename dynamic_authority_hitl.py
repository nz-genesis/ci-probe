"""Clean-room dynamic-authority + HITL + irreversibility experiment.

The experiment asks whether approval at one time is sufficient when authority can
be revoked before an irreversible realization. Two realization strategies are
compared: snapshot authority and revalidation at the realization boundary.
"""

from dataclasses import dataclass
from enum import Enum


class Mechanism(str, Enum):
    SNAPSHOT = "snapshot-authority"
    REVALIDATE = "revalidate-at-realization"


class Outcome(str, Enum):
    EXECUTED = "executed"
    BLOCKED_REVOKED = "blocked-revoked"
    PENDING_HUMAN = "pending-human"
    UNKNOWN_AFTER_EFFECT = "unknown-after-effect"


@dataclass(frozen=True)
class Proposal:
    request_id: str
    irreversible: bool
    approved_by_human: bool
    authority_at_request: bool
    authority_at_realization: bool
    acknowledgement: bool
    effect_observed: bool


@dataclass(frozen=True)
class Observation:
    mechanism: Mechanism
    outcome: Outcome
    effect_count: int
    reconciliation_required: bool


def realize(proposal: Proposal, mechanism: Mechanism) -> Observation:
    if not proposal.approved_by_human:
        return Observation(mechanism, Outcome.PENDING_HUMAN, 0, False)

    if mechanism is Mechanism.REVALIDATE and not proposal.authority_at_realization:
        return Observation(mechanism, Outcome.BLOCKED_REVOKED, 0, False)

    if mechanism is Mechanism.SNAPSHOT and not proposal.authority_at_request:
        return Observation(mechanism, Outcome.BLOCKED_REVOKED, 0, False)

    if not proposal.acknowledgement and not proposal.effect_observed:
        return Observation(mechanism, Outcome.UNKNOWN_AFTER_EFFECT, 1, True)

    return Observation(mechanism, Outcome.EXECUTED, 1, False)


APPROVED_NO_REVOCATION = Proposal(
    "req-001", True, True, True, True, True, True
)

REVOKED_BEFORE_REALIZATION = Proposal(
    "req-002", True, True, True, False, True, False
)

PENDING_HUMAN = Proposal(
    "req-003", True, False, True, True, False, False
)

LATE_ACK_LOST_AFTER_EFFECT = Proposal(
    "req-004", True, True, True, True, False, False
)


def verify() -> None:
    stable_snapshot = realize(APPROVED_NO_REVOCATION, Mechanism.SNAPSHOT)
    stable_revalidate = realize(APPROVED_NO_REVOCATION, Mechanism.REVALIDATE)
    assert stable_snapshot.outcome == stable_revalidate.outcome == Outcome.EXECUTED

    revoked_snapshot = realize(REVOKED_BEFORE_REALIZATION, Mechanism.SNAPSHOT)
    revoked_revalidate = realize(REVOKED_BEFORE_REALIZATION, Mechanism.REVALIDATE)

    # This is the discriminating counterexample: snapshotting approval is not
    # semantically equivalent to checking authority at the irreversible boundary.
    assert revoked_snapshot.outcome == Outcome.EXECUTED
    assert revoked_revalidate.outcome == Outcome.BLOCKED_REVOKED
    assert revoked_snapshot.effect_count == 1
    assert revoked_revalidate.effect_count == 0

    pending = realize(PENDING_HUMAN, Mechanism.REVALIDATE)
    assert pending.outcome == Outcome.PENDING_HUMAN
    assert pending.effect_count == 0

    unknown = realize(LATE_ACK_LOST_AFTER_EFFECT, Mechanism.REVALIDATE)
    assert unknown.outcome == Outcome.UNKNOWN_AFTER_EFFECT
    assert unknown.reconciliation_required is True


if __name__ == "__main__":
    verify()
    print("dynamic authority + HITL: PASS")
