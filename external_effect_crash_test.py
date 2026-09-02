"""Executable checks for external-effect reconciliation."""

from external_effect_crash import (
    Authority,
    EffectEvidence,
    Record,
    Reconciliation,
    Transition,
    reconcile,
    verify,
)


def test_invariants() -> None:
    verify()


def test_crash_with_lost_ack_is_unknown() -> None:
    record = Record(Authority.VALID, Transition.INITIATED, EffectEvidence.NONE, False)
    assert reconcile(record) is Reconciliation.EFFECT_UNKNOWN


def test_revocation_after_initiation_does_not_erase_effect() -> None:
    record = Record(Authority.REVOKED, Transition.INITIATED, EffectEvidence.OCCURRED, False)
    assert reconcile(record) is Reconciliation.EFFECT_CONFIRMED


def test_ack_is_not_effect_verification() -> None:
    record = Record(Authority.VALID, Transition.INITIATED, EffectEvidence.NONE, True)
    assert reconcile(record) is Reconciliation.EFFECT_UNKNOWN


def test_absence_requires_distinct_evidence() -> None:
    absent = Record(Authority.REVOKED, Transition.INITIATED, EffectEvidence.ABSENT, False)
    unknown = Record(Authority.REVOKED, Transition.INITIATED, EffectEvidence.NONE, False)
    assert reconcile(absent) is Reconciliation.EFFECT_ABSENT
    assert reconcile(unknown) is Reconciliation.EFFECT_UNKNOWN


def test_conflicting_effect_evidence_is_preserved() -> None:
    record = Record(Authority.REVOKED, Transition.INITIATED, EffectEvidence.CONFLICTING, False)
    assert reconcile(record) is Reconciliation.EFFECT_CONFLICTING


if __name__ == "__main__":
    test_invariants()
    test_crash_with_lost_ack_is_unknown()
    test_revocation_after_initiation_does_not_erase_effect()
    test_ack_is_not_effect_verification()
    test_absence_requires_distinct_evidence()
    test_conflicting_effect_evidence_is_preserved()
    print("external effect crash: PASS")
