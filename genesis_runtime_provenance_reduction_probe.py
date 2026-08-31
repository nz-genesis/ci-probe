"""Public-safe clean-room probe for causal evidence reduction.

No private Genesis state, witness material, authority payloads, corpus, or
private identifiers are used. The probe tests only generic evidence properties:
causal binding is stronger than ordering alone, duplicate evidence is not
mistaken for a new effect, conflicts are rejected, and admissible evidence is
not promoted to world truth.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Evidence:
    transition_id: str
    source_id: str
    sequence: int
    causal_token: str
    attested: bool
    digest: str


def token_only(previous: Evidence | None, candidate: Evidence) -> bool:
    if not candidate.transition_id or not candidate.source_id:
        return False
    if not candidate.attested or not candidate.causal_token or not candidate.digest:
        return False
    if previous is None:
        return True
    if candidate.source_id != previous.source_id:
        return False
    if candidate.causal_token != previous.causal_token:
        return False
    if candidate.digest != previous.digest:
        return False
    return True


def sequence_only(previous: Evidence | None, candidate: Evidence) -> bool:
    if not candidate.transition_id or not candidate.source_id:
        return False
    if not candidate.attested or not candidate.digest:
        return False
    if previous is None:
        return True
    return candidate.source_id == previous.source_id and candidate.sequence > previous.sequence


def main() -> None:
    base = Evidence("t1", "source-a", 7, "attempt-a", True, "digest-a")
    same = Evidence("t1", "source-a", 7, "attempt-a", True, "digest-a")
    stale = Evidence("t1", "source-a", 6, "attempt-old", True, "digest-old")
    source_swap = Evidence("t1", "source-b", 8, "attempt-a", True, "digest-a")
    causal_swap = Evidence("t1", "source-a", 8, "attempt-b", True, "digest-b")
    conflict = Evidence("t1", "source-a", 8, "attempt-a", True, "digest-b")
    unattested = Evidence("t1", "source-a", 8, "attempt-a", False, "digest-a")

    assert token_only(None, base)
    # Identical evidence is idempotently admissible; it must not be interpreted
    # as permission for a second external realization.
    assert token_only(base, same)
    assert not token_only(base, stale)
    assert not token_only(base, source_swap)
    assert not token_only(base, causal_swap)
    assert not token_only(base, conflict)
    assert not token_only(base, unattested)

    # Sequence alone demonstrates the reduction gap: a higher sequence can be
    # accepted even when its causal token belongs to another attempt.
    unrelated_higher_sequence = Evidence("t1", "source-a", 8, "unrelated", True, "digest-b")
    assert sequence_only(base, unrelated_higher_sequence)
    assert not token_only(base, unrelated_higher_sequence)

    # The probe intentionally does not define a VERIFIED state. A true return
    # value means only that the evidence satisfies this public test's admissibility
    # relation; it is never a claim that the external world changed.
    print("GENESIS RUNTIME PROVENANCE REDUCTION: PASS")
    print("Invariant: causal binding rejects the sequence-only false positive")


if __name__ == "__main__":
    main()
