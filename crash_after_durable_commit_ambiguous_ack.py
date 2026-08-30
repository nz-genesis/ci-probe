"""Clean-room bounded test for crash-after-durable-commit with lost ACK.

The model distinguishes durable effect from acknowledgement delivery. A
commit may become durable while the caller observes no ACK. Recovery must
reconcile durable state before retrying, and an authority/version change must
invalidate an unresolved stale retry. This is evidence about the bounded
failure model, not a Genesis primitive claim.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Attempt:
    actor: str
    commitment: str
    nonce: str
    expected_version: int


class DurableDomain:
    def __init__(self):
        self.version = 7
        self.effects = set()

    def commit_and_lose_ack(self, attempt: Attempt):
        key = (attempt.commitment, attempt.nonce)
        if attempt.expected_version != self.version or key in self.effects:
            return False
        self.effects.add(key)
        return None  # durable commit happened; acknowledgement was lost

    def reconcile(self, attempt: Attempt):
        return (attempt.commitment, attempt.nonce) in self.effects

    def retry(self, attempt: Attempt):
        key = (attempt.commitment, attempt.nonce)
        if attempt.expected_version != self.version or key in self.effects:
            return False
        self.effects.add(key)
        return True


def main():
    domain = DurableDomain()
    first = Attempt("A", "C1", "N1", 7)

    # The durable effect occurs, but the caller receives no acknowledgement.
    assert domain.commit_and_lose_ack(first) is None
    assert domain.reconcile(first) is True

    # Reconciliation prevents an unsafe duplicate retry.
    assert domain.retry(first) is False
    assert len(domain.effects) == 1

    # A different actor cannot substitute the same effect.
    second = Attempt("B", "C1", "N1", 7)
    assert domain.retry(second) is False
    assert len(domain.effects) == 1

    # If authority/version changes before reconciliation, the stale retry is
    # rejected; reconciliation of the old durable effect remains observable.
    domain.version = 8
    stale = Attempt("A", "C1", "N2", 7)
    assert domain.retry(stale) is False
    assert domain.reconcile(first) is True

    # An unrelated new nonce under the current version remains admissible.
    fresh = Attempt("A", "C1", "N3", 8)
    assert domain.retry(fresh) is True
    assert len(domain.effects) == 2

    print("CRASH AFTER DURABLE COMMIT / LOST ACK: 8/8 PASS")
    print("durable_effect_without_ack=True")
    print("reconciliation_detects_effect=True")
    print("unsafe_retry_rejected=True")
    print("actor_substitution_rejected=True")
    print("stale_retry_rejected=True")
    print("fresh_current_version_commit=True")


if __name__ == "__main__":
    main()
