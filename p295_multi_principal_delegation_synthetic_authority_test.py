from dataclasses import dataclass
from itertools import combinations


@dataclass(frozen=True)
class Root:
    root_id: str
    epoch: int


@dataclass(frozen=True)
class Delegation:
    principal: str
    issuer_root: str
    subject: str
    epoch: int
    scope: str
    active: bool


@dataclass(frozen=True)
class Credential:
    principal: str
    root: str
    epoch: int
    scope: str


PROTECTED_ROOTS = {"R1", "R2"}
PROTECTED_EPOCH = 7
REQUIRED_PRINCIPALS = {"A", "B"}
SCOPE = "change"


def valid_credential(c: Credential, roots: set[Root], delegations: set[Delegation]) -> bool:
    if Root(c.root, c.epoch) not in roots:
        return False
    if c.root not in PROTECTED_ROOTS or c.epoch != PROTECTED_EPOCH:
        return False
    if c.scope != SCOPE:
        return False
    return any(
        d.principal == c.principal
        and d.issuer_root == c.root
        and d.subject == c.principal
        and d.epoch == c.epoch
        and d.scope == c.scope
        and d.active
        for d in delegations
    )


def authorized_quorum(credentials: set[Credential], roots: set[Root], delegations: set[Delegation]) -> bool:
    valid = {c.principal for c in credentials if valid_credential(c, roots, delegations)}
    # The protected policy names the principals; arbitrary composition is not enough.
    return REQUIRED_PRINCIPALS.issubset(valid)


def main():
    roots = {Root("R1", PROTECTED_EPOCH), Root("R2", PROTECTED_EPOCH)}
    delegations = {
        Delegation("A", "R1", "A", PROTECTED_EPOCH, SCOPE, True),
        Delegation("B", "R2", "B", PROTECTED_EPOCH, SCOPE, True),
        Delegation("C", "R1", "C", PROTECTED_EPOCH, SCOPE, True),
        Delegation("A", "R1", "A", PROTECTED_EPOCH - 1, SCOPE, True),
        Delegation("B", "R2", "B", PROTECTED_EPOCH, "read", True),
        Delegation("A", "R-EVIL", "A", PROTECTED_EPOCH, SCOPE, True),
    }

    a = Credential("A", "R1", PROTECTED_EPOCH, SCOPE)
    b = Credential("B", "R2", PROTECTED_EPOCH, SCOPE)
    c = Credential("C", "R1", PROTECTED_EPOCH, SCOPE)
    stale_a = Credential("A", "R1", PROTECTED_EPOCH - 1, SCOPE)
    wrong_scope_b = Credential("B", "R2", PROTECTED_EPOCH, "read")
    evil_a = Credential("A", "R-EVIL", PROTECTED_EPOCH, SCOPE)

    # 1. Independently valid credentials from the two protected roots satisfy the named quorum.
    assert authorized_quorum({a, b}, roots, delegations)

    # 2. One valid principal cannot satisfy a two-principal protected policy.
    assert not authorized_quorum({a}, roots, delegations)

    # 3. Two credentials for the same principal do not synthesize a second principal.
    assert not authorized_quorum({a, Credential("A", "R2", PROTECTED_EPOCH, SCOPE)}, roots, delegations)

    # 4. A valid credential from an unprotected root cannot contribute to the quorum.
    assert not authorized_quorum({a, evil_a}, roots, delegations)

    # 5. Stale delegation/credential cannot survive the protected epoch boundary.
    assert not authorized_quorum({stale_a, b}, roots, delegations)

    # 6. A delegated credential with the wrong scope cannot authorize a change.
    assert not authorized_quorum({a, wrong_scope_b}, roots, delegations)

    # 7. An unrelated but valid principal cannot replace a named required principal.
    assert not authorized_quorum({a, c}, roots, delegations)

    # 8. Duplicate presentations of the same credential do not increase authority.
    assert not authorized_quorum({a, a}, roots, delegations)

    # 9. Removing B's active delegation breaks the quorum even though B's credential is well formed.
    revoked_b = {d for d in delegations if not (d.principal == "B" and d.issuer_root == "R2" and d.scope == SCOPE)}
    assert not authorized_quorum({a, b}, roots, revoked_b)

    # 10. Adding an attacker-controlled root to the ordinary root set cannot override the protected root set.
    roots_with_attacker = roots | {Root("R-EVIL", PROTECTED_EPOCH)}
    assert not authorized_quorum({a, evil_a}, roots_with_attacker, delegations)

    # 11. All valid principal subsets are evaluated explicitly; only {A,B} authorizes the protected quorum.
    candidates = {a, b, c}
    authorized_sets = {
        frozenset(x) for n in range(1, len(candidates) + 1)
        for x in combinations(candidates, n)
        if authorized_quorum(set(x), roots, delegations)
    }
    assert authorized_sets == {frozenset({a, b}), frozenset({a, b, c})}

    # 12. A synthetic root cannot replace a named required principal.
    synthetic = Credential("SYNTHETIC", "R-SYNTH", PROTECTED_EPOCH, SCOPE)
    assert not authorized_quorum({a, synthetic}, roots | {Root("R-SYNTH", PROTECTED_EPOCH)}, delegations)

    # 13. Root rotation requires the new protected epoch/root set; old credentials do not carry forward.
    new_roots = {Root("R1", PROTECTED_EPOCH + 1), Root("R2", PROTECTED_EPOCH + 1)}
    assert not authorized_quorum({a, b}, new_roots, delegations)

    # 14. Protected policy remains explicit after all adversarial inputs.
    assert PROTECTED_ROOTS == {"R1", "R2"}
    assert REQUIRED_PRINCIPALS == {"A", "B"}
    assert SCOPE == "change"

    print("P295 multi-principal delegation / synthetic authority: 14/14 PASS")


if __name__ == "__main__":
    main()
