"""Clean-room L6d: authority-root lifecycle and temporal validity.

The experiment keeps authority/admission separate from execution/effect. It
asks whether a root's later revocation/compromise changes the authority claim
for a decision made before that event, and whether uncertainty is preserved
when the ordering is unavailable.
"""
from dataclasses import dataclass
from enum import Enum


class RootStatus(str, Enum):
    TRUSTED = "trusted"
    REVOKED = "revoked"
    COMPROMISED = "compromised"
    UNKNOWN = "unknown"
    CONFLICTING = "conflicting"


@dataclass(frozen=True)
class AuthorityEvidence:
    status: RootStatus
    at: int
    valid: bool = True


def authority_at(evidence: tuple[AuthorityEvidence, ...], decision_at: int) -> RootStatus:
    usable = tuple(item for item in evidence if item.valid and item.at <= decision_at)
    if not usable:
        return RootStatus.UNKNOWN

    latest_at = max(item.at for item in usable)
    latest = tuple(item for item in usable if item.at == latest_at)
    statuses = {item.status for item in latest}

    if len(statuses) > 1:
        return RootStatus.CONFLICTING
    return next(iter(statuses))


def verify() -> None:
    trusted = (AuthorityEvidence(RootStatus.TRUSTED, 10),)
    revoked = trusted + (AuthorityEvidence(RootStatus.REVOKED, 20),)
    compromised = trusted + (AuthorityEvidence(RootStatus.COMPROMISED, 20),)

    # Revocation/compromise after the decision does not retroactively rewrite
    # the historical authority state at the earlier decision boundary.
    assert authority_at(revoked, 15) is RootStatus.TRUSTED
    assert authority_at(compromised, 15) is RootStatus.TRUSTED

    # At/after the lifecycle event, the latest valid evidence governs.
    assert authority_at(revoked, 20) is RootStatus.REVOKED
    assert authority_at(compromised, 20) is RootStatus.COMPROMISED

    # No evidence at the decision boundary is not authorization.
    assert authority_at((), 20) is RootStatus.UNKNOWN
    assert authority_at((AuthorityEvidence(RootStatus.TRUSTED, 30),), 20) is RootStatus.UNKNOWN

    # Conflicting evidence at the same decision boundary remains explicit.
    conflict = (
        AuthorityEvidence(RootStatus.TRUSTED, 20),
        AuthorityEvidence(RootStatus.REVOKED, 20),
    )
    assert authority_at(conflict, 20) is RootStatus.CONFLICTING

    # Invalid evidence cannot create certainty.
    invalid = (AuthorityEvidence(RootStatus.TRUSTED, 20, valid=False),)
    assert authority_at(invalid, 20) is RootStatus.UNKNOWN


if __name__ == "__main__":
    verify()
    print("ROOT LIFECYCLE AUTHORITY 6/6 PASS")
