"""Clean-room bounded test for coordinated one-time consumption.

The experiment distinguishes verifier-local replay protection from a shared
coordination domain. Raw observations are intentionally numeric/opaque; the
asserted property is that one shared-domain commit wins under a deterministic
race, while retries after a committed consume do not create a second consume.
This is evidence about the tested coordination model, not a Genesis primitive.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Attempt:
    verifier: str
    commitment: str
    nonce: str
    expected_version: int


class SharedDomain:
    def __init__(self):
        self.version = 7
        self.consumed = set()

    def prepare(self, attempt: Attempt):
        return (attempt.commitment, attempt.nonce) not in self.consumed and attempt.expected_version == self.version

    def commit(self, attempt: Attempt):
        key = (attempt.commitment, attempt.nonce)
        if attempt.expected_version != self.version or key in self.consumed:
            return False
        self.consumed.add(key)
        return True


def main():
    a = Attempt("A", "C1", "N1", 7)
    b = Attempt("B", "C1", "N1", 7)
    domain = SharedDomain()

    # Both actors may observe an admissible pre-state.
    assert domain.prepare(a) is True
    assert domain.prepare(b) is True

    # Adversarial interleaving: A commits first, B commits second.
    assert domain.commit(a) is True
    assert domain.commit(b) is False

    # Duplicate delivery and retry remain rejected.
    assert domain.commit(a) is False
    assert domain.commit(b) is False

    # A version change cannot be consumed using the old precondition.
    c = Attempt("C", "C1", "N2", 6)
    assert domain.prepare(c) is False
    assert domain.commit(c) is False

    print("SHARED DOMAIN ATOMIC CONSUMPTION: 5/5 PASS")
    print("both_prepared=True")
    print("exactly_one_commit=True")
    print("retries_rejected=True")
    print("stale_version_rejected=True")


if __name__ == "__main__":
    main()
