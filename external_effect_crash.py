"""Clean-room experiment: external effect, crash window, and reconciliation.

The model deliberately separates authority, transition state, effect evidence,
and acknowledgement. Recovery is represented as reconciliation over those
states rather than as a dedicated execution/recovery primitive.
"""

from dataclasses import dataclass
from enum import Enum


class Authority(str, Enum):
    VALID = "valid"
    REVOKED = "revoked"


class Transition(str, Enum):
    NOT_STARTED = "not-started"
    INITIATED = "initiated"
    TERMINATED = "terminated"


class EffectEvidence(str, Enum):
    NONE = "none"
    OCCURRED = "occurred"
    ABSENT = "absent"
    CONFLICTING = "conflicting"


class Reconciliation(str, Enum):
    NO_EFFECT_KNOWN = "no-effect-known"
    EFFECT_CONFIRMED = "effect-confirmed"
    EFFECT_ABSENT = "effect-absent"
    EFFECT_UNKNOWN = "effect-unknown"
    EFFECT_CONFLICTING = "effect-conflicting"


@dataclass(frozen=True)
class Record:
    authority: Authority
    transition: Transition
    effect: EffectEvidence
    acknowledgement: bool


def reconcile(record: Record) -> Reconciliation:
    if record.effect is EffectEvidence.OCCURRED:
        return Reconciliation.EFFECT_CONFIRMED
    if record.effect is EffectEvidence.ABSENT:
        return Reconciliation.EFFECT_ABSENT
    if record.effect is EffectEvidence.CONFLICTING:
        return Reconciliation.EFFECT_CONFLICTING
    if record.transition is Transition.INITIATED:
        return Reconciliation.EFFECT_UNKNOWN
    return Reconciliation.NO_EFFECT_KNOWN


def verify() -> None:
    # Valid authority + initiation + crash + lost acknowledgement does not
    # prove either occurrence or absence of the external effect.
    crashed_unknown = Record(
        Authority.VALID, Transition.INITIATED, EffectEvidence.NONE, False
    )
    assert reconcile(crashed_unknown) is Reconciliation.EFFECT_UNKNOWN

    # Late evidence can confirm the effect even after authority is revoked.
    late_confirmed = Record(
        Authority.REVOKED, Transition.INITIATED, EffectEvidence.OCCURRED, False
    )
    assert reconcile(late_confirmed) is Reconciliation.EFFECT_CONFIRMED

    # Revocation after initiation does not retroactively prove that the effect
    # did not occur.
    assert reconcile(late_confirmed) is not Reconciliation.EFFECT_ABSENT

    # Explicit non-effect evidence is distinct from missing evidence.
    absent = Record(
        Authority.REVOKED, Transition.INITIATED, EffectEvidence.ABSENT, False
    )
    assert reconcile(absent) is Reconciliation.EFFECT_ABSENT
    assert reconcile(crashed_unknown) is not Reconciliation.EFFECT_ABSENT

    # Conflicting evidence remains conflicting.
    conflict = Record(
        Authority.REVOKED, Transition.INITIATED, EffectEvidence.CONFLICTING, False
    )
    assert reconcile(conflict) is Reconciliation.EFFECT_CONFLICTING

    # Acknowledgement alone does not establish effect occurrence.
    acknowledged_without_effect_evidence = Record(
        Authority.VALID, Transition.INITIATED, EffectEvidence.NONE, True
    )
    assert reconcile(acknowledged_without_effect_evidence) is Reconciliation.EFFECT_UNKNOWN

    # No initiation means there is no basis in this model to claim an effect.
    not_started = Record(
        Authority.VALID, Transition.NOT_STARTED, EffectEvidence.NONE, False
    )
    assert reconcile(not_started) is Reconciliation.NO_EFFECT_KNOWN


if __name__ == "__main__":
    verify()
    print("external effect crash: PASS")
