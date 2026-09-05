from dataclasses import dataclass
from enum import Enum

class Verdict(Enum):
    VALID = "valid"
    INVALID = "invalid"
    UNKNOWN = "unknown"

@dataclass(frozen=True)
class RecoveryAuthority:
    epoch: int
    signers: frozenset[str]
    threshold: int
    protected: bool = True

@dataclass(frozen=True)
class RecoveryCertificate:
    parent_epoch: int
    new_epoch: int
    new_signers: frozenset[str]
    signers: frozenset[str]


def certify(parent: RecoveryAuthority, cert: RecoveryCertificate) -> Verdict:
    if not parent.protected:
        return Verdict.UNKNOWN
    if cert.parent_epoch != parent.epoch or cert.new_epoch != parent.epoch + 1:
        return Verdict.INVALID
    if not cert.signers <= parent.signers:
        return Verdict.INVALID
    return Verdict.VALID if len(cert.signers) >= parent.threshold else Verdict.UNKNOWN


def choose_converged(certs: list[RecoveryCertificate], parent: RecoveryAuthority) -> Verdict:
    valid = [c for c in certs if certify(parent, c) is Verdict.VALID]
    if not valid:
        return Verdict.UNKNOWN
    targets = {(c.new_epoch, c.new_signers) for c in valid}
    return Verdict.VALID if len(targets) == 1 else Verdict.UNKNOWN


def run() -> None:
    a1 = RecoveryAuthority(1, frozenset({"r1", "r2", "r3", "b"}), 3)
    a2 = frozenset({"r2", "r3", "r4", "r5"})
    a2_alt = frozenset({"r1", "r2", "r4", "r5"})

    good = RecoveryCertificate(1, 2, a2, frozenset({"r1", "r2", "r3"}))
    bad_epoch = RecoveryCertificate(1, 3, a2, frozenset({"r1", "r2", "r3"}))
    forged = RecoveryCertificate(1, 2, frozenset({"attacker"}), frozenset({"attacker", "r1", "r2"}))
    weak = RecoveryCertificate(1, 2, a2, frozenset({"r1", "r2"}))
    alt = RecoveryCertificate(1, 2, a2_alt, frozenset({"r1", "r2", "r3"}))

    assert certify(a1, good) is Verdict.VALID
    assert certify(a1, bad_epoch) is Verdict.INVALID
    assert certify(a1, forged) is Verdict.INVALID
    assert certify(a1, weak) is Verdict.UNKNOWN

    # Two individually quorum-valid conflicting successor authorities cannot
    # be selected by Genesis without an independent convergence rule.
    assert choose_converged([good], a1) is Verdict.VALID
    assert choose_converged([good, alt], a1) is Verdict.UNKNOWN

    compromised = RecoveryAuthority(2, frozenset({"attacker"}), 1, protected=False)
    forged_parent = RecoveryCertificate(2, 3, frozenset({"attacker", "r9"}), frozenset({"attacker"}))
    assert certify(compromised, forged_parent) is Verdict.UNKNOWN

    # A recovery authority cannot silently skip its predecessor epoch.
    skipped = RecoveryCertificate(2, 4, frozenset({"r9", "r10", "r11"}), frozenset({"r1", "r2", "r3"}))
    assert certify(a1, skipped) is Verdict.INVALID

    print("P278 recovery authority rotation: 8/8 PASS")

if __name__ == "__main__":
    run()
