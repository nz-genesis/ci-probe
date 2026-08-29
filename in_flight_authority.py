"""Clean-room L6e: authority loss while realization is in flight.

The probe separates authority state, realization state, external effect,
and verification. It deliberately does not infer absence of effect from
cancellation or authority revocation.
"""
from dataclasses import dataclass
from enum import Enum


class Outcome(str, Enum):
    AUTHORIZED = "authorized"
    REVOKED = "revoked"
    UNKNOWN = "unknown"
    EXECUTING = "executing"
    CANCELLED = "cancelled"
    EFFECT_OBSERVED = "effect_observed"
    NO_EFFECT_VERIFIED = "no_effect_verified"
    CONFLICTING = "conflicting"


@dataclass(frozen=True)
class Event:
    kind: str
    at: int
    valid: bool = True


def authority_at(events: tuple[Event, ...], at: int) -> Outcome:
    usable = tuple(e for e in events if e.valid and e.kind in {"authorized", "revoked"} and e.at <= at)
    if not usable:
        return Outcome.UNKNOWN
    latest_at = max(e.at for e in usable)
    latest = {e.kind for e in usable if e.at == latest_at}
    if len(latest) > 1:
        return Outcome.CONFLICTING
    return Outcome.AUTHORIZED if "authorized" in latest else Outcome.REVOKED


def effect_state(events: tuple[Event, ...], at: int) -> Outcome:
    usable = tuple(e for e in events if e.valid and e.at <= at)
    if any(e.kind == "effect_observed" for e in usable):
        return Outcome.EFFECT_OBSERVED
    if any(e.kind == "no_effect_verified" for e in usable):
        return Outcome.NO_EFFECT_VERIFIED
    return Outcome.UNKNOWN


def verify() -> None:
    authorized = (Event("authorized", 10),)
    revoked_before_execution = authorized + (Event("revoked", 20),)

    # Admission/authority at the realization boundary can change before
    # execution begins; this does not retroactively create an effect.
    assert authority_at(revoked_before_execution, 15) is Outcome.AUTHORIZED
    assert authority_at(revoked_before_execution, 20) is Outcome.REVOKED
    assert effect_state((), 20) is Outcome.UNKNOWN

    # Revocation while execution is in flight is not equivalent to failure or
    # absence of an external effect.
    in_flight = revoked_before_execution + (Event("executing", 21),)
    assert authority_at(in_flight, 21) is Outcome.REVOKED
    assert effect_state(in_flight, 21) is Outcome.UNKNOWN

    # Cancellation provides no proof that an external effect did not occur.
    cancelled = in_flight + (Event("cancelled", 22),)
    assert effect_state(cancelled, 22) is Outcome.UNKNOWN

    # An observed effect remains an effect even if cancellation happened first.
    effect_after_cancel = cancelled + (Event("effect_observed", 23),)
    assert effect_state(effect_after_cancel, 23) is Outcome.EFFECT_OBSERVED

    # Only explicit verification can establish absence of effect.
    no_effect = cancelled + (Event("no_effect_verified", 24),)
    assert effect_state(no_effect, 24) is Outcome.NO_EFFECT_VERIFIED

    # Conflicting authority evidence remains explicit.
    conflict = (
        Event("authorized", 20),
        Event("revoked", 20),
    )
    assert authority_at(conflict, 20) is Outcome.CONFLICTING

    # Future or invalid evidence cannot create current certainty.
    assert authority_at((Event("revoked", 30),), 20) is Outcome.UNKNOWN
    assert authority_at((Event("authorized", 20, valid=False),), 20) is Outcome.UNKNOWN


if __name__ == "__main__":
    verify()
    print("IN-FLIGHT AUTHORITY 9/9 PASS")
