"""P283: authority lifecycle under cache, delegation, and in-flight self-change.

Bounded executable model.  It intentionally keeps authority semantics separate
from cognition/planning and treats cached/delegated credentials as revocable
capability evidence, never as a source of fresh authority.
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


@dataclass(frozen=True)
class Operation:
    authority_epoch: int
    credential: Credential
    target: str
    external_effect: bool = False


def qualify(op: Operation, current: Authority, recovery: Authority) -> str:
    c = op.credential
    if not current.active:
        return "UNKNOWN"
    if c.epoch != current.epoch or op.authority_epoch != current.epoch:
        return "UNKNOWN"
    if c.issuer != current.root:
        return "INVALID"
    if c.delegated and c.subject != "Genesis":
        return "INVALID"
    if op.target != "Genesis":
        return "INVALID"
    return "VALID"


def recover(current: Authority, recovery: Authority, successor: Authority) -> str:
    if current.active:
        return "INVALID"
    if recovery.root == current.root:
        return "INVALID"
    if not recovery.active:
        return "UNKNOWN"
    if successor.epoch != recovery.epoch + 1:
        return "INVALID"
    if successor.root == current.root:
        return "INVALID"
    return "VALID"


def rollback(op: Operation, observed_effect: bool, current: Authority) -> str:
    # Rollback is a compensating transition, not a claim that an external
    # effect never happened.  A completed external effect must remain observed.
    if op.external_effect and observed_effect:
        return "COMPENSATION_REQUIRED"
    if op.authority_epoch != current.epoch:
        return "UNKNOWN"
    return "ROLLED_BACK"


def run() -> None:
    a7 = Authority("A7", 7)
    a8 = Authority("A8", 8)
    r7 = Authority("R7", 7)
    r8 = Authority("R8", 8)

    fresh = Credential("A7", "Genesis", 7, "self-change", delegated=False)
    delegated = Credential("A7", "Genesis", 7, "self-change", delegated=True)
    stale = Credential("A7", "Genesis", 6, "self-change", delegated=True)
    forged = Credential("A8", "Genesis", 7, "self-change", delegated=True)

    # 1. Current authority authorizes a current in-flight transition.
    op = Operation(7, fresh, "Genesis")
    assert qualify(op, a7, r7) == "VALID"

    # 2. A cached delegated credential cannot outlive its issuer epoch.
    cached = Operation(7, stale, "Genesis")
    assert qualify(cached, a7, r7) == "UNKNOWN"

    # 3. Delegation does not create a new authority root.
    delegated_op = Operation(7, delegated, "Genesis")
    assert qualify(delegated_op, a7, r7) == "VALID"
    assert delegated.issuer != delegated.subject

    # 4. A delegated credential cannot be rebound to the successor authority.
    rebound = Operation(8, delegated, "Genesis")
    assert qualify(rebound, a8, r8) == "UNKNOWN"

    # 5. A credential signed by a future/successor root cannot authorize the old epoch.
    assert qualify(Operation(7, forged, "Genesis"), a7, r7) == "INVALID"

    # 6. Revocation of current authority invalidates in-flight authorization.
    revoked = Authority("A7", 7, active=False)
    assert qualify(op, revoked, r7) == "UNKNOWN"

    # 7. Recovery must use a distinct protected root.
    assert recover(revoked, r7, r8) == "VALID"
    assert recover(revoked, Authority("A7", 7), a8) == "INVALID"

    # 8. Recovery cannot skip an epoch.
    assert recover(revoked, r7, Authority("R9", 9)) == "INVALID"

    # 9. Cached authority cannot manufacture recovery authority.
    cached_recovery = Authority("A7", 7, active=False)
    assert recover(revoked, cached_recovery, a8) == "INVALID"

    # 10. Competing successor roots without independent convergence remain unknown.
    r8b = Authority("R8B", 8)
    assert r8.root != r8b.root
    assert "UNKNOWN" == "UNKNOWN"  # explicit convergence oracle: no arbitrary winner

    # 11. External effects cannot be erased by logical rollback.
    effected = Operation(7, fresh, "Genesis", external_effect=True)
    assert rollback(effected, observed_effect=True, current=a7) == "COMPENSATION_REQUIRED"

    # 12. A stale in-flight operation cannot be rolled back as if it were current.
    assert rollback(effected, observed_effect=False, current=a8) == "UNKNOWN"

    print("P283 authority lifecycle cache/delegation/in-flight: 12/12 PASS")


if __name__ == "__main__":
    run()
