"""Clean-room bounded test for crash-after-prepare recovery.

The model separates preparation from durable consumption. A crash after
prepare leaves no consumed marker; recovery may retry. The commit operation
is the only transition that records consumption, and the transition is
idempotent for the same (commitment, nonce). This is evidence about the
bounded recovery model, not a Genesis primitive claim.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Attempt:
    actor: str
    commitment: str
    nonce: str
    expected_version: int


class RecoverableDomain:
    def __init__(self):
        self.version = 7
        self.consumed = set()

    def prepare(self, attempt: Attempt):
        return attempt.expected_version == self.version and (attempt.commitment, attempt.nonce) not in self.consumed

    def crash_after_prepare(self):
        # Volatile preparation state is discarded by the crash.
        return None

    def commit(self, attempt: Attempt):
        key = (attempt.commitment, attempt.nonce)
        if attempt.expected_version != self.version or key in self.consumed:
            return False
        self.consumed.add(key)
        return True


def main():
    first = Attempt("A", "C1", "N1", 7)
    domain = RecoverableDomain()

    assert domain.prepare(first) is True
    domain.crash_after_prepare()

    # Recovery can safely retry because preparation was not consumption.
    assert domain.prepare(first) is True
    assert domain.commit(first) is True

    # A duplicate retry after durable consumption remains rejected.
    assert domain.prepare(first) is False
    assert domain.commit(first) is False

    # A second actor cannot turn the crashed preparation into a second consume.
    second = Attempt("B", "C1", "N1", 7)
    assert domain.prepare(second) is False
    assert domain.commit(second) is False

    # An old-version recovery attempt is rejected after a version change.
    domain.version = 8
    stale = Attempt("A", "C1", "N2", 7)
    assert domain.prepare(stale) is False
    assert domain.commit(stale) is False

    print("CRASH AFTER PREPARE RECOVERY: 8/8 PASS")
    print("prepare_before_crash=True")
    print("retry_after_crash=True")
    print("exactly_one_durable_commit=True")
    print("post_commit_retry_rejected=True")
    print("second_actor_rejected=True")
    print("stale_recovery_rejected=True")


if __name__ == "__main__":
    main()
