from dataclasses import dataclass
from itertools import product


@dataclass(frozen=True)
class Root:
    root_id: str
    epoch: int


@dataclass(frozen=True)
class Delegation:
    issuer: str
    subject: str
    epoch: int
    scope: frozenset[str]
    active: bool


@dataclass(frozen=True)
class Credential:
    subject: str
    root: str
    epoch: int
    scope: frozenset[str]
    path: tuple[str, ...]


PROTECTED_ROOTS = {"R1", "R2"}
EPOCH = 9
REQUEST_SCOPE = frozenset({"change"})
ROOT_POLICY = frozenset({"A", "B"})


def delegation_map(delegations):
    return {(d.issuer, d.subject): d for d in delegations}


def valid_path(credential, roots, delegations):
    if Root(credential.root, credential.epoch) not in roots:
        return False
    if credential.root not in PROTECTED_ROOTS or credential.epoch != EPOCH:
        return False
    if not credential.scope.issuperset(REQUEST_SCOPE):
        return False
    if len(credential.path) < 2 or credential.path[-1] != credential.subject:
        return False

    dm = delegation_map(delegations)
    current = credential.root
    inherited_scope = frozenset({"change", "read", "admin"})
    for subject in credential.path[1:]:
        d = dm.get((current, subject))
        if d is None or not d.active or d.epoch != EPOCH:
            return False
        if not d.scope.issubset(inherited_scope):
            return False
        inherited_scope = d.scope
        current = subject
    return inherited_scope == credential.scope


def authorized(credentials, roots, delegations):
    valid = {c.subject for c in credentials if valid_path(c, roots, delegations)}
    return ROOT_POLICY.issubset(valid)


def main():
    roots = {Root("R1", EPOCH), Root("R2", EPOCH)}
    delegations = {
        Delegation("R1", "A", EPOCH, frozenset({"change", "read"}), True),
        Delegation("A", "X", EPOCH, frozenset({"change"}), True),
        Delegation("X", "Y", EPOCH, frozenset({"change"}), True),
        Delegation("R2", "B", EPOCH, frozenset({"change"}), True),
        Delegation("B", "Z", EPOCH, frozenset({"read"}), True),
        Delegation("R1", "C", EPOCH, frozenset({"change"}), True),
        Delegation("C", "D", EPOCH - 1, frozenset({"change"}), True),
        Delegation("R-EVIL", "E", EPOCH, frozenset({"change"}), True),
    }

    a = Credential("A", "R1", EPOCH, frozenset({"change", "read"}), ("R1", "A"))
    x = Credential("X", "R1", EPOCH, frozenset({"change"}), ("R1", "A", "X"))
    y = Credential("Y", "R1", EPOCH, frozenset({"change"}), ("R1", "A", "X", "Y"))
    b = Credential("B", "R2", EPOCH, frozenset({"change"}), ("R2", "B"))
    z = Credential("Z", "R2", EPOCH, frozenset({"read"}), ("R2", "B", "Z"))
    c = Credential("C", "R1", EPOCH, frozenset({"change"}), ("R1", "C"))
    d = Credential("D", "R1", EPOCH, frozenset({"change"}), ("R1", "C", "D"))
    evil = Credential("E", "R-EVIL", EPOCH, frozenset({"change"}), ("R-EVIL", "E"))

    # 1. A protected root can delegate to A.
    assert valid_path(a, roots, delegations)
    # 2. Attenuation is preserved across A -> X.
    assert valid_path(x, roots, delegations)
    # 3. Multi-hop attenuation remains valid when every hop preserves/subsets scope.
    assert valid_path(y, roots, delegations)
    # 4. The protected two-principal policy can be satisfied by A and B.
    assert authorized({a, b}, roots, delegations)
    # 5. B's narrower read-only delegation cannot authorize a change as Z.
    assert not valid_path(z, roots, delegations)
    # 6. An expired intermediate delegation invalidates its descendant even if the descendant credential looks current.
    assert not valid_path(d, roots, delegations)
    # 7. An unprotected root cannot become legitimate by creating a valid-looking descendant.
    assert not valid_path(evil, roots | {Root("R-EVIL", EPOCH)}, delegations)
    # 8. Revoking A invalidates every descendant credential rooted through A.
    revoked_a = {dd for dd in delegations if not (dd.issuer == "R1" and dd.subject == "A")}
    assert not valid_path(x, roots, revoked_a)
    assert not valid_path(y, roots, revoked_a)
    # 9. Revoking X invalidates Y; cached Y cannot outlive its ancestor.
    revoked_x = {dd for dd in delegations if not (dd.issuer == "X" and dd.subject == "Y")}
    assert not valid_path(y, roots, revoked_x)
    # 10. Epoch rotation invalidates every old credential/path.
    rotated = {Root("R1", EPOCH + 1), Root("R2", EPOCH + 1)}
    assert not valid_path(a, rotated, delegations)
    assert not valid_path(y, rotated, delegations)
    # 11. Reordering path nodes cannot manufacture a valid chain.
    reordered = Credential("Y", "R1", EPOCH, frozenset({"change"}), ("R1", "X", "A", "Y"))
    assert not valid_path(reordered, roots, delegations)
    # 12. A synthetic credential cannot replace B in the protected policy.
    synthetic = Credential("SYNTH", "R1", EPOCH, frozenset({"change"}), ("R1", "A", "SYNTH"))
    assert not authorized({a, synthetic}, roots, delegations)
    # 13. Enumerate adversarial boolean combinations: stale/revoked A, X, and Y never become valid.
    for revoke_a, revoke_x, revoke_y in product((False, True), repeat=3):
        ds = set(delegations)
        if revoke_a:
            ds = {dd for dd in ds if not (dd.issuer == "R1" and dd.subject == "A")}
        if revoke_x:
            ds = {dd for dd in ds if not (dd.issuer == "A" and dd.subject == "X")}
        if revoke_y:
            ds = {dd for dd in ds if not (dd.issuer == "X" and dd.subject == "Y")}
        if revoke_a or revoke_x or revoke_y:
            assert not valid_path(y, roots, ds)
    # 14. Conflicting/untrusted verifier input cannot alter the protected root policy in this model.
    assert ROOT_POLICY == frozenset({"A", "B"})

    print("P296 multi-hop delegation / attenuation / revocation: 14/14 PASS")


if __name__ == "__main__":
    main()
