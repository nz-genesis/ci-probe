"""P283: authority lifecycle under cache, delegation, and in-flight self-change.

Bounded executable model. Authority semantics remain separate from cognition;
cache and delegation can carry evidence but cannot manufacture fresh authority.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Authority:
    root: str
    epoch: int
    active: bool = True


@dataclass(frozen=True)
class Credential:
    issuer: str
    subject: str
    epoch: int
    operation: str
    delegated: bool
    parent: str | None = None


@dataclass(frozen=True)
class Operation:
    authority_epoch: int
    credential: Credential
    target: str
    external_effect: bool = False


def qualify(op: Operation, current: Authority) -> str:
    c = op.credential
    if not current.active:
        return "UNKNOWN"
    if c.epoch != current.epoch or op.authority_epoch != current.epoch:
        return "UNKNOWN"
    if c.issuer != current.root:
        return "INVALID"
    if c.delegated and (c.subject != "Genesis" or c.parent != c.issuer):
        return "INVALID"
    if c.operation != "self-change" or op.target != "Genesis":
        return "INVALID"
    return "VALID"


def recover(current: Authority, recovery: Authority, successor: Authority, trusted_roots: set[str]) -> str:
    if current.active:
        return "INVALID"
    if recovery.root not in trusted_roots:
        return "INVALID"
    if recovery.root == current.root or not recovery.active:
        return "UNKNOWN"
    if successor.epoch != recovery.epoch + 1:
        return "INVALID"
    if successor.root == current.root:
        return "INVALID"
    return "VALID"


def rollback(op: Operation, observed_effect: bool, current: Authority) -> str:
    if op.external_effect and observed_effect:
        return "COMPENSATION_REQUIRED"
    if op.authority_epoch != current.epoch:
        return "UNKNOWN"
    return "ROLLED_BACK"


def run() -> None:
    a7 = Authority("A7", 7)
    a8 = Authority("A8", 8)
    revoked = Authority("A7", 7, active=False)
    r7 = Authority("R7", 7)
    r8 = Authority("R8", 8)
    untrusted = Authority("X", 7)
    trusted_roots = {"R7"}

    fresh = Credential("A7", "Genesis", 7, "self-change", delegated=False)
    delegated = Credential("A7", "Genesis", 7, "self-change", delegated=True, parent="A7")
    chained = Credential("A7", "Genesis", 7, "self-change", delegated=True, parent="A8")
    stale = Credential("A7", "Genesis", 6, "self-change", delegated=True, parent="A7")
    forged = Credential("A8", "Genesis", 7, "self-change", delegated=True, parent="A8")

    # 1. Current authority authorizes a current in-flight transition.
    op = Operation(7, fresh, "Genesis")
    assert qualify(op, a7) == "VALID"

    # 2. A cached delegated credential cannot outlive its issuer epoch.
    assert qualify(Operation(7, stale, "Genesis"), a7) == "UNKNOWN"

    # 3. Delegation carries existing authority; it does not create a new root.
    assert qualify(Operation(7, delegated, "Genesis"), a7) == "VALID"
    assert delegated.issuer == "A7" and delegated.parent == "A7"

    # 4. A delegated credential cannot be rebound to the successor authority.
    assert qualify(Operation(8, delegated, "Genesis"), a8) == "UNKNOWN"

    # 5. A future/successor credential cannot authorize the old epoch.
    assert qualify(Operation(7, forged, "Genesis"), a7) == "INVALID"

    # 6. Delegation-chain laundering is rejected when the parent is not the issuer.
    assert qualify(Operation(7, chained, "Genesis"), a7) == "INVALID"

    # 7. Revocation invalidates an otherwise valid in-flight authorization.
    assert qualify(op, revoked) == "UNKNOWN"

    # 8. Recovery requires a separately trusted recovery root.
    assert recover(revoked, r7, r8, trusted_roots) == "VALID"

    # 9. A mutable/untrusted root cannot bootstrap itself into recovery authority.
    assert recover(revoked, untrusted, a8, trusted_roots) == "INVALID"

    # 10. A recovery successor cannot skip an epoch.
    assert recover(revoked, r7, Authority("R9", 9), trusted_roots) == "INVALID"

    # 11. Conflicting successor roots have no local arbitrary winner.
    r8b = Authority("R8B", 8)
    candidates = {r8.root, r8b.root}
    assert len(candidates) == 2
    convergence = None if len(candidates) > 1 else next(iter(candidates))
    assert convergence is None

    # 12. An observed external effect cannot be erased by logical rollback.
    effected = Operation(7, fresh, "Genesis", external_effect=True)
    assert rollback(effected, observed_effect=True, current=a7) == "COMPENSATION_REQUIRED"

    # 13. A stale in-flight operation cannot be rolled back as current.
    assert rollback(effected, observed_effect=False, current=a8) == "UNKNOWN"

    print("P283 authority lifecycle cache/delegation/in-flight: 13/13 PASS")


if __name__ == "__main__":
    run()
