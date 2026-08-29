"""Clean-room authority uncertainty experiment.

Authority state is derived from evidence rather than represented as a new
primitive. Conflicting or missing evidence is kept distinct from authorization.
"""

from enum import Enum


class AuthorityState(str, Enum):
    AUTHORIZED = "authorized"
    REVOKED = "revoked"
    UNKNOWN = "unknown"
    CONFLICTING = "conflicting"


class Mechanism(str, Enum):
    OPTIMISTIC = "optimistic"
    FAIL_CLOSED = "fail-closed"


def derive_state(valid_evidence: bool, revoked_evidence: bool) -> AuthorityState:
    if valid_evidence and revoked_evidence:
        return AuthorityState.CONFLICTING
    if valid_evidence:
        return AuthorityState.AUTHORIZED
    if revoked_evidence:
        return AuthorityState.REVOKED
    return AuthorityState.UNKNOWN


def admit(state: AuthorityState, mechanism: Mechanism) -> bool:
    if mechanism is Mechanism.OPTIMISTIC:
        return state in (AuthorityState.AUTHORIZED, AuthorityState.UNKNOWN)
    return state is AuthorityState.AUTHORIZED


def verify() -> None:
    assert derive_state(True, False) == AuthorityState.AUTHORIZED
    assert derive_state(False, True) == AuthorityState.REVOKED
    assert derive_state(False, False) == AuthorityState.UNKNOWN
    assert derive_state(True, True) == AuthorityState.CONFLICTING

    assert admit(AuthorityState.AUTHORIZED, Mechanism.FAIL_CLOSED) is True
    assert admit(AuthorityState.REVOKED, Mechanism.FAIL_CLOSED) is False
    assert admit(AuthorityState.UNKNOWN, Mechanism.FAIL_CLOSED) is False
    assert admit(AuthorityState.CONFLICTING, Mechanism.FAIL_CLOSED) is False

    # The optimistic strategy is a deliberate counterexample for uncertainty.
    assert admit(AuthorityState.UNKNOWN, Mechanism.OPTIMISTIC) is True
    assert admit(AuthorityState.CONFLICTING, Mechanism.OPTIMISTIC) is False


if __name__ == "__main__":
    verify()
    print("authority uncertainty: PASS")
