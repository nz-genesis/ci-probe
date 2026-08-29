"""Regression suite for L6d root lifecycle authority."""
from root_lifecycle_authority import AuthorityEvidence, RootStatus, authority_at


def test_pre_event_authority_is_historical() -> None:
    evidence = (
        AuthorityEvidence(RootStatus.TRUSTED, 10),
        AuthorityEvidence(RootStatus.REVOKED, 20),
    )
    assert authority_at(evidence, 15) is RootStatus.TRUSTED


def test_revocation_applies_at_boundary() -> None:
    evidence = (
        AuthorityEvidence(RootStatus.TRUSTED, 10),
        AuthorityEvidence(RootStatus.REVOKED, 20),
    )
    assert authority_at(evidence, 20) is RootStatus.REVOKED


def test_compromise_applies_at_boundary() -> None:
    evidence = (
        AuthorityEvidence(RootStatus.TRUSTED, 10),
        AuthorityEvidence(RootStatus.COMPROMISED, 20),
    )
    assert authority_at(evidence, 20) is RootStatus.COMPROMISED


def test_no_evidence_is_unknown() -> None:
    assert authority_at((), 20) is RootStatus.UNKNOWN


def test_future_evidence_is_not_used() -> None:
    evidence = (AuthorityEvidence(RootStatus.TRUSTED, 30),)
    assert authority_at(evidence, 20) is RootStatus.UNKNOWN


def test_same_boundary_conflict_is_explicit() -> None:
    evidence = (
        AuthorityEvidence(RootStatus.TRUSTED, 20),
        AuthorityEvidence(RootStatus.REVOKED, 20),
    )
    assert authority_at(evidence, 20) is RootStatus.CONFLICTING


def test_invalid_evidence_is_not_authorization() -> None:
    evidence = (AuthorityEvidence(RootStatus.TRUSTED, 20, valid=False),)
    assert authority_at(evidence, 20) is RootStatus.UNKNOWN


if __name__ == "__main__":
    tests = (
        test_pre_event_authority_is_historical,
        test_revocation_applies_at_boundary,
        test_compromise_applies_at_boundary,
        test_no_evidence_is_unknown,
        test_future_evidence_is_not_used,
        test_same_boundary_conflict_is_explicit,
        test_invalid_evidence_is_not_authorization,
    )
    for test in tests:
        test()
    print("ROOT LIFECYCLE AUTHORITY REGRESSION 7/7 PASS")
