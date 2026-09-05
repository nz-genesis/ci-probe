from dataclasses import dataclass
from enum import Enum

class V(Enum):
    VALID = 1
    INVALID = 2
    UNKNOWN = 3

@dataclass(frozen=True)
class Root:
    id: str
    epoch: int
    protected: bool

@dataclass(frozen=True)
class RecoveryEvidence:
    recovery_root: str
    old_root: str
    new_root: str
    new_epoch: int
    signers: frozenset[str]

@dataclass(frozen=True)
class RecoveryAuthority:
    root: Root
    signers: frozenset[str]
    threshold: int


def authorize_recovery(old: Root, new: Root, evidence: RecoveryEvidence,
                       authority: RecoveryAuthority) -> V:
    if not authority.root.protected:
        return V.UNKNOWN
    if evidence.recovery_root != authority.root.id:
        return V.INVALID
    if evidence.old_root != old.id or evidence.new_root != new.id:
        return V.INVALID
    if evidence.new_epoch != old.epoch + 1:
        return V.INVALID
    if not evidence.signers <= authority.signers:
        return V.INVALID
    return V.VALID if len(evidence.signers) >= authority.threshold else V.UNKNOWN


def run():
    current = Root("A1", 7, True)
    independent = Root("RECOVERY", 42, True)
    next_root = Root("A2", 8, True)
    auth = RecoveryAuthority(independent, frozenset({"r1", "r2", "r3"}), 2)

    # P276 tests provenance of recovery authority, not cryptographic establishment.
    good = RecoveryEvidence("RECOVERY", "A1", "A2", 8, frozenset({"r1", "r2"}))
    assert authorize_recovery(current, next_root, good, auth) is V.VALID

    # Current Genesis authority cannot manufacture the independent recovery root.
    circular = RecoveryEvidence("A1", "A1", "A2", 8, frozenset({"r1", "r2"}))
    assert authorize_recovery(current, next_root, circular, auth) is V.INVALID

    # A compromised mutable representation cannot become a trusted recovery root.
    compromised = RecoveryAuthority(Root("RECOVERY", 42, False), frozenset({"attacker"}), 1)
    forged = RecoveryEvidence("RECOVERY", "A1", "A2", 8, frozenset({"attacker"}))
    assert authorize_recovery(current, next_root, forged, compromised) is V.UNKNOWN

    # Evidence is target-bound and cannot be replayed for another successor.
    other = RecoveryEvidence("RECOVERY", "A1", "EVIL", 8, frozenset({"r1", "r2"}))
    assert authorize_recovery(current, next_root, other, auth) is V.INVALID

    # Epoch skipping is forbidden.
    a3 = Root("A3", 9, True)
    skipped = RecoveryEvidence("RECOVERY", "A1", "A3", 9, frozenset({"r1", "r2"}))
    assert authorize_recovery(current, a3, skipped, auth) is V.INVALID

    # Missing quorum remains UNKNOWN rather than becoming guessed authority.
    insufficient = RecoveryEvidence("RECOVERY", "A1", "A2", 8, frozenset({"r1"}))
    assert authorize_recovery(current, next_root, insufficient, auth) is V.UNKNOWN

    # Recovery authority is not ordinary execution authority.
    assert auth.root.id != next_root.id

    print("P276 recovery-authority provenance: 7/7 PASS")

if __name__ == "__main__":
    run()
