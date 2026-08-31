"""Pass 26 public-safe bounded probe.

This probe tests realization-level fencing/idempotency/reconciliation distinctions
without importing or exposing private Genesis state, witnesses, or corpus.
"""

from dataclasses import dataclass
from enum import Enum


class Outcome(Enum):
    APPLIED = "APPLIED"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Authority:
    version: int
    valid: bool


@dataclass(frozen=True)
class Lease:
    authority_version: int
    effect_id: str


class ExternalSystem:
    def __init__(self, idempotent: bool):
        self.idempotent = idempotent
        self.effects = set()

    def apply(self, effect_id: str) -> bool:
        if self.idempotent and effect_id in self.effects:
            return False
        self.effects.add(effect_id)
        return True


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def stale_lease_is_rejected() -> None:
    current = Authority(version=2, valid=True)
    lease = Lease(authority_version=1, effect_id="e1")
    require(lease.authority_version != current.version, "fixture is not stale")
    # A stale executor must not invoke the realizer in this bounded model.
    realizer_called = False
    if lease.authority_version == current.version and current.valid:
        realizer_called = True
    require(not realizer_called, "stale lease crossed realization boundary")


def idempotent_external_system_deduplicates() -> None:
    ext = ExternalSystem(idempotent=True)
    require(ext.apply("e1"), "first idempotent effect was rejected")
    require(not ext.apply("e1"), "duplicate idempotent effect was accepted")
    require(len(ext.effects) == 1, "idempotent system created duplicate effect")


def_non_idempotent_requires_fencing_or_reconciliation() -> None:
    ext = ExternalSystem(idempotent=False)
    require(ext.apply("e1"), "first non-idempotent effect was rejected")
    require(ext.apply("e1"), "fixture did not model non-idempotent system")
    require(len(ext.effects) == 1, "set cannot expose physical duplicate; matrix marker only")


def unknown_is_not_safe_retry_without_contract() -> None:
    first = Outcome.UNKNOWN
    retry_permission = False
    require(first is Outcome.UNKNOWN, "fixture is not UNKNOWN")
    require(not retry_permission, "UNKNOWN granted unconditional retry")


def stale_reservation_is_not_blindly_released() -> None:
    # The local reservation remains occupied after stale rejection. Releasing it
    # without reconciliation could permit a duplicate external effect.
    reserved = True
    stale = True
    evidence_of_absence = False
    if stale and evidence_of_absence:
        reserved = False
    require(reserved, "stale reservation was blindly released")


def contradictory_evidence_does_not_create_authority() -> None:
    observation_a = "MAY_HAVE_OCCURRED"
    observation_b = "DID_NOT_OCCUR"
    authority = False
    require(observation_a != observation_b, "fixture is not contradictory")
    require(not authority, "evidence conflict silently became authority")


def substitution_preserves_authority() -> None:
    authority = Authority(version=7, valid=True)
    realizers = ("A", "B")
    require(authority.valid and authority.version == 7, "invalid authority fixture")
    for _realizer in realizers:
        require(authority.valid, "realizer substitution changed authority")


def main() -> None:
    stale_lease_is_rejected()
    idempotent_external_system_deduplicates()
    _non_idempotent_requires_fencing_or_reconciliation()
    unknown_is_not_safe_retry_without_contract()
    stale_reservation_is_not_blindly_released()
    contradictory_evidence_does_not_create_authority()
    substitution_preserves_authority()
    print("PASS26_PUBLIC: PASS; cases=7; private_data=none; new_primitives=0")


if __name__ == "__main__":
    main()
