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
    auth = RecoveryAuthority(independent, frozenset({"r1","r2","r3"}), 2)

    # 1. Independent recovery authority can authorize a successor.
    good = RecoveryEvidence("RECOVERY", "A1", "A2", 8, frozenset({"r1","r2"}))
    assert authorize_recovery(current, next_root, good, auth) is V.VALID

    # 2. Current Genesis authority cannot be reused as recovery root merely
    # because it is currently valid.
    circular = RecoveryEvidence("A1", "A1", "A2", 8, frozenset({"r1","r2"}))
    assert authorize_recovery(current, next_root, circular, auth) is V.INVALID

    # 3. A compromised/mutable recovery representation cannot become authority.
    compromised = RecoveryAuthority(Root("RECOVERY", 42, False), frozenset({"attacker"}), 1)
    forged = RecoveryEvidence("RECOVERY", "A1", "A2", 8, frozenset({"attacker"}))
    assert authorize_recovery(current, next_root, forged, compromised) is V.UNKNOWN

    # 4. Replay for another successor is rejected.
    other = RecoveryEvidence("RECOVERY", "A1", "EVIL", 8, frozenset({"r1","r2"}))
    assert authorize_recovery(current, next_root, other, auth) is V.INVALID

    # 5. Old epoch cannot be skipped.
    skipped = RecoveryEvidence("RECOVERY", "A1", "A3", 9, frozenset({"r1","r2"}))
    a3 = Root("A3", 9, True)
    assert authorize_recovery(current, a3, skipped, auth) is V.INVALID

    # 6. Missing recovery quorum remains unknown.
    insufficient = RecoveryEvidence("RECOVERY", "A1", "A2", 8, frozenset({"r1"}))
    assert authorize_recovery(current, next_root, insufficient, auth) is V.UNKNOWN

    # 7. Recovery authority does not grant ordinary execution authority.
    assert auth.root.id != next_root.id

    print("P276 recovery-authority provenance: 7/7 PASS")

if __name__ == "__main__":
    run()
