from dataclasses import dataclass


@dataclass(frozen=True)
class Verifier:
    name: str
    root: str
    epoch: int
    policy_version: int
    policy_digest: str
    required: frozenset[str]
    trusted: bool


@dataclass(frozen=True)
class Credential:
    subject: str
    root: str
    epoch: int
    scope: frozenset[str]
    policy_version: int


PROTECTED_ROOTS = frozenset({"R1", "R2"})
CURRENT_EPOCH = 10
CURRENT_POLICY_VERSION = 2
PROTECTED_POLICY = frozenset({"A", "B"})
PROTECTED_POLICY_DIGEST = "policy-v2-A+B"
CHANGE = frozenset({"change"})


def verify(v: Verifier, c: Credential) -> bool:
    return (
        v.trusted and v.root in PROTECTED_ROOTS
        and v.epoch == CURRENT_EPOCH
        and v.policy_version == CURRENT_POLICY_VERSION
        and v.policy_digest == PROTECTED_POLICY_DIGEST
        and c.root in PROTECTED_ROOTS and c.epoch == CURRENT_EPOCH
        and c.policy_version == CURRENT_POLICY_VERSION
        and c.scope.issuperset(CHANGE)
    )


def decision(v: Verifier, credentials):
    valid = {c.subject for c in credentials if verify(v, c)}
    return v.required.issubset(valid)


def authorized(verifiers, credentials):
    trusted = [v for v in verifiers if v.trusted and v.root in PROTECTED_ROOTS]
    if not trusted:
        return False
    if any(v.epoch != CURRENT_EPOCH or v.policy_version != CURRENT_POLICY_VERSION for v in trusted):
        return False
    if len({v.policy_digest for v in trusted}) != 1:
        return False
    if trusted[0].policy_digest != PROTECTED_POLICY_DIGEST:
        return False
    decisions = [decision(v, credentials) for v in trusted]
    return len(set(decisions)) == 1 and decisions[0]


def main():
    v1 = Verifier("V1", "R1", CURRENT_EPOCH, CURRENT_POLICY_VERSION, PROTECTED_POLICY_DIGEST, PROTECTED_POLICY, True)
    v2 = Verifier("V2", "R2", CURRENT_EPOCH, CURRENT_POLICY_VERSION, PROTECTED_POLICY_DIGEST, PROTECTED_POLICY, True)
    permissive = Verifier("V-permissive", "R1", CURRENT_EPOCH, CURRENT_POLICY_VERSION, "policy-v2-A-only", frozenset({"A"}), True)
    stale = Verifier("V-stale", "R1", CURRENT_EPOCH, 1, "policy-v1", PROTECTED_POLICY, True)
    evil_root = Verifier("V-evil", "EVIL", CURRENT_EPOCH, CURRENT_POLICY_VERSION, PROTECTED_POLICY_DIGEST, PROTECTED_POLICY, True)
    a = Credential("A", "R1", CURRENT_EPOCH, CHANGE, CURRENT_POLICY_VERSION)
    b = Credential("B", "R2", CURRENT_EPOCH, CHANGE, CURRENT_POLICY_VERSION)
    e = Credential("E", "EVIL", CURRENT_EPOCH, CHANGE, CURRENT_POLICY_VERSION)
    old_b = Credential("B", "R2", CURRENT_EPOCH, CHANGE, 1)
    old_a = Credential("A", "R1", CURRENT_EPOCH - 1, CHANGE, CURRENT_POLICY_VERSION)

    # 1. Current trusted verifiers converge on the protected policy.
    assert authorized([v1, v2], [a, b])
    # 2. A permissive policy view cannot replace the protected policy.
    assert not authorized([v1, permissive], [a])
    # 3. A permissive verifier cannot launder an untrusted principal into the policy.
    assert not authorized([v1, permissive], [a, e])
    # 4. A stale verifier dependency fails closed.
    assert not authorized([v1, stale], [a, b])
    # 5. An unprotected verifier root cannot authorize the protected transition.
    assert not authorized([evil_root], [a, b])
    # 6. Missing B cannot be synthesized by E.
    assert not authorized([v1, v2], [a, e])
    # 7. Wrong policy version is stale evidence.
    assert not authorized([v1, v2], [a, old_b])
    # 8. Wrong epoch is stale evidence.
    assert not authorized([v1, v2], [old_a, b])
    # 9. Duplicate presentation cannot satisfy two distinct principals.
    assert not authorized([v1, v2], [a, a])
    # 10. Stale extra credentials do not poison current convergent evidence.
    assert authorized([v1, v2], [a, b, old_a, old_b])
    # 11. Explicit verifier policy disagreement must fail closed.
    assert not authorized([v1, permissive], [a, b])
    # 12. A forged verifier with a trusted-looking name but wrong root is rejected.
    forged = Verifier("V1", "EVIL", CURRENT_EPOCH, CURRENT_POLICY_VERSION, PROTECTED_POLICY_DIGEST, PROTECTED_POLICY, True)
    assert not authorized([forged], [a, b])
    # 13. Two verifiers cannot manufacture a third protected root through credentials.
    assert not authorized([v1, v2], [a, e])
    # 14. No trusted verifier means fail closed.
    assert not authorized([], [a, b])

    print("P297 distributed verifier disagreement / stale dependency: 14/14 PASS")


if __name__ == "__main__":
    main()
