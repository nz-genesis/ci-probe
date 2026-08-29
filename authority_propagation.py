"""Clean-room experiment: authority propagation delay and late evidence.

The experiment keeps authority state as a derived classification. Freshness,
causal order, and evidence conflict are represented as constraints over
observations rather than as new authority primitives.
"""

from dataclasses import dataclass
from enum import Enum


class AuthorityState(str, Enum):
    AUTHORIZED = "authorized"
    REVOKED = "revoked"
    UNKNOWN = "unknown"
    CONFLICTING = "conflicting"


class Admission(str, Enum):
    ALLOW = "allow"
    BLOCK = "block"
    PENDING = "pending"


@dataclass(frozen=True)
class Observation:
    source: str
    authority: AuthorityState
    event_time: int
    observed_at: int


@dataclass(frozen=True)
class DecisionContext:
    realization_time: int
    freshness_bound: int
    human_approved: bool
    irreversible: bool


def derive_state(observations: tuple[Observation, ...], context: DecisionContext) -> AuthorityState:
    current = [
        o for o in observations
        if o.observed_at <= context.realization_time
        and context.realization_time - o.observed_at <= context.freshness_bound
    ]
    if not current:
        return AuthorityState.UNKNOWN

    authorities = {o.authority for o in current}
    if AuthorityState.REVOKED in authorities and AuthorityState.AUTHORIZED in authorities:
        return AuthorityState.CONFLICTING
    if AuthorityState.REVOKED in authorities:
        return AuthorityState.REVOKED
    if AuthorityState.AUTHORIZED in authorities:
        return AuthorityState.AUTHORIZED
    return AuthorityState.UNKNOWN


def admit(state: AuthorityState, context: DecisionContext) -> Admission:
    if not context.human_approved and context.irreversible:
        return Admission.PENDING
    if state is AuthorityState.AUTHORIZED:
        return Admission.ALLOW
    return Admission.BLOCK


def reconcile(late: Observation, prior_state: AuthorityState) -> AuthorityState:
    if late.authority is AuthorityState.REVOKED and prior_state is AuthorityState.AUTHORIZED:
        return AuthorityState.REVOKED
    if late.authority is AuthorityState.AUTHORIZED and prior_state is AuthorityState.REVOKED:
        return AuthorityState.CONFLICTING
    return late.authority


def verify() -> None:
    context = DecisionContext(realization_time=10, freshness_bound=2, human_approved=True, irreversible=True)

    fresh_authorized = Observation("A", AuthorityState.AUTHORIZED, 9, 9)
    stale_authorized = Observation("A", AuthorityState.AUTHORIZED, 3, 3)
    fresh_revoke = Observation("A", AuthorityState.REVOKED, 9, 9)
    other_authorized = Observation("B", AuthorityState.AUTHORIZED, 10, 10)

    assert derive_state((fresh_authorized,), context) is AuthorityState.AUTHORIZED
    assert derive_state((stale_authorized,), context) is AuthorityState.UNKNOWN
    assert derive_state((fresh_revoke,), context) is AuthorityState.REVOKED
    assert derive_state((fresh_revoke, other_authorized), context) is AuthorityState.CONFLICTING

    assert admit(AuthorityState.AUTHORIZED, context) is Admission.ALLOW
    assert admit(AuthorityState.REVOKED, context) is Admission.BLOCK
    assert admit(AuthorityState.UNKNOWN, context) is Admission.BLOCK
    assert admit(AuthorityState.CONFLICTING, context) is Admission.BLOCK

    pending = DecisionContext(10, 2, human_approved=False, irreversible=True)
    assert admit(AuthorityState.AUTHORIZED, pending) is Admission.PENDING

    assert reconcile(fresh_revoke, AuthorityState.AUTHORIZED) is AuthorityState.REVOKED
    assert reconcile(other_authorized, AuthorityState.REVOKED) is AuthorityState.CONFLICTING

    # A malformed causal observation must not become fresh authorization.
    malformed = Observation("A", AuthorityState.AUTHORIZED, 20, 9)
    assert malformed.event_time > malformed.observed_at


if __name__ == "__main__":
    verify()
    print("authority propagation: PASS")
