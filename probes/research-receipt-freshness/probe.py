#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from enum import Enum


class Verdict(str, Enum):
    ADMISSIBLE = "ADMISSIBLE"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class Receipt:
    cryptographically_valid: bool
    source_version_current: bool | None
    trust_generation_current: bool | None
    dependency_revision_current: bool | None
    authority_current: bool | None
    scope_matches: bool | None
    policy_allows: bool | None
    time_fresh: bool | None
    historical_qualification_allowed: bool


def qualify_current(r: Receipt) -> Verdict:
    # Cryptographic validity is necessary but never sufficient.
    if not r.cryptographically_valid:
        return Verdict.REJECTED
    checks = (
        r.source_version_current,
        r.trust_generation_current,
        r.dependency_revision_current,
        r.authority_current,
        r.scope_matches,
        r.policy_allows,
        r.time_fresh,
    )
    if any(x is False for x in checks):
        return Verdict.REJECTED
    if any(x is None for x in checks):
        return Verdict.UNKNOWN
    return Verdict.ADMISSIBLE


def qualify_historical(r: Receipt) -> Verdict:
    # Historical qualification deliberately does not inherit current trust.
    if not r.cryptographically_valid:
        return Verdict.REJECTED
    return (
        Verdict.ADMISSIBLE
        if r.historical_qualification_allowed
        else Verdict.REJECTED
    )


def test_exhaustive_tri_state_space() -> int:
    states = (False, True, None)
    count = 0
    for values in product(states, repeat=7):
        r = Receipt(
            cryptographically_valid=True,
            source_version_current=values[0],
            trust_generation_current=values[1],
            dependency_revision_current=values[2],
            authority_current=values[3],
            scope_matches=values[4],
            policy_allows=values[5],
            time_fresh=values[6],
            historical_qualification_allowed=True,
        )
        verdict = qualify_current(r)
        assert verdict in set(Verdict)
        if all(v is True for v in values):
            assert verdict is Verdict.ADMISSIBLE
        elif any(v is False for v in values):
            assert verdict is Verdict.REJECTED
        else:
            assert verdict is Verdict.UNKNOWN
        count += 1
    return count


def test_crypto_validity_is_not_current_admissibility() -> None:
    base = Receipt(True, True, True, True, True, True, True, True, True)
    stale = Receipt(True, True, False, True, True, True, True, True, True)
    assert qualify_current(base) is Verdict.ADMISSIBLE
    assert qualify_current(stale) is Verdict.REJECTED
    assert qualify_historical(stale) is Verdict.ADMISSIBLE


def test_recovery_preserves_history_but_changes_current_admissibility() -> None:
    before = Receipt(True, True, True, True, True, True, True, True, True)
    after_rotation = Receipt(True, True, False, True, True, True, True, True, True)
    assert qualify_historical(before) is Verdict.ADMISSIBLE
    assert qualify_historical(after_rotation) is Verdict.ADMISSIBLE
    assert qualify_current(before) is Verdict.ADMISSIBLE
    assert qualify_current(after_rotation) is Verdict.REJECTED


def test_unknown_freshness_cannot_be_upgraded_to_admissible() -> None:
    unavailable = Receipt(True, True, None, True, True, True, True, True, True)
    assert qualify_current(unavailable) is Verdict.UNKNOWN


def test_scope_and_policy_are_distinct_from_integrity() -> None:
    wrong_scope = Receipt(True, True, True, True, True, False, True, True, True)
    denied_policy = Receipt(True, True, True, True, True, True, False, True, True)
    assert qualify_current(wrong_scope) is Verdict.REJECTED
    assert qualify_current(denied_policy) is Verdict.REJECTED


def test_current_authority_change_does_not_rewrite_history() -> None:
    old_authority = Receipt(True, True, True, True, True, True, True, True, True)
    revoked_now = Receipt(True, True, True, True, False, True, True, True, True)
    assert qualify_historical(old_authority) is Verdict.ADMISSIBLE
    assert qualify_historical(revoked_now) is Verdict.ADMISSIBLE
    assert qualify_current(revoked_now) is Verdict.REJECTED


def test_time_freshness_is_policy_input_not_signature_property() -> None:
    expired = Receipt(True, True, True, True, True, True, True, False, True)
    assert qualify_current(expired) is Verdict.REJECTED
    assert qualify_historical(expired) is Verdict.ADMISSIBLE


def test_no_single_external_mechanism_can_define_genesis_authority() -> None:
    # Signature/trust state is an input to qualification, not the semantic
    # authority itself. Removing current authority must change admissibility
    # without invalidating the historical cryptographic fact.
    r = Receipt(True, True, True, True, False, True, True, True, True)
    assert qualify_historical(r) is Verdict.ADMISSIBLE
    assert qualify_current(r) is Verdict.REJECTED


def run() -> None:
    cases = test_exhaustive_tri_state_space()
    test_crypto_validity_is_not_current_admissibility()
    test_recovery_preserves_history_but_changes_current_admissibility()
    test_unknown_freshness_cannot_be_upgraded_to_admissible()
    test_scope_and_policy_are_distinct_from_integrity()
    test_current_authority_change_does_not_rewrite_history()
    test_time_freshness_is_policy_input_not_signature_property()
    test_no_single_external_mechanism_can_define_genesis_authority()
    print(f"RECEIPT_FRESHNESS_CASES={cases}")
    print("HISTORICAL_VALIDITY_SEPARATION=PASS")
    print("CURRENT_ADMISSIBILITY_SEPARATION=PASS")
    print("UNKNOWN_FRESHNESS_PRESERVED=PASS")
    print("RECOVERY_HISTORY_PRESERVED=PASS")
    print("AUTHORITY_POLICY_SEPARATION=PASS")
    print("RECEIPT_FRESHNESS_BOUNDARY=PASS")


if __name__ == "__main__":
    run()
