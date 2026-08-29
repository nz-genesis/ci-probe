from in_flight_authority import Event, Outcome, authority_at, effect_state


def test_revocation_before_execution_does_not_create_effect():
    events = (Event("authorized", 10), Event("revoked", 20))
    assert authority_at(events, 20) is Outcome.REVOKED
    assert effect_state(events, 20) is Outcome.UNKNOWN


def test_revocation_during_in_flight_is_not_failure_or_no_effect():
    events = (
        Event("authorized", 10),
        Event("executing", 20),
        Event("revoked", 21),
    )
    assert authority_at(events, 21) is Outcome.REVOKED
    assert effect_state(events, 21) is Outcome.UNKNOWN


def test_cancellation_does_not_prove_absence_of_effect():
    events = (Event("executing", 20), Event("cancelled", 21))
    assert effect_state(events, 21) is Outcome.UNKNOWN


def test_effect_after_cancellation_remains_observable():
    events = (
        Event("executing", 20),
        Event("cancelled", 21),
        Event("effect_observed", 22),
    )
    assert effect_state(events, 22) is Outcome.EFFECT_OBSERVED


def test_verified_no_effect_is_distinct_from_cancellation():
    events = (
        Event("executing", 20),
        Event("cancelled", 21),
        Event("no_effect_verified", 22),
    )
    assert effect_state(events, 22) is Outcome.NO_EFFECT_VERIFIED


def test_conflicting_authority_is_not_resolved_by_orderless_latest_claim():
    events = (Event("authorized", 20), Event("revoked", 20))
    assert authority_at(events, 20) is Outcome.CONFLICTING


def test_future_evidence_is_not_current_authority():
    assert authority_at((Event("revoked", 30),), 20) is Outcome.UNKNOWN


def test_invalid_authority_evidence_is_not_current_authority():
    assert authority_at((Event("authorized", 20, valid=False),), 20) is Outcome.UNKNOWN
