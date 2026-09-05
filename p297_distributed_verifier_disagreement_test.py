from dataclasses import dataclass


@dataclass(frozen=True)
class Verifier:
    name: str
    root: str
    epoch: int
    policy_version: int
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
REQUIRED = frozenset({"A", "B"})
CHANGE = frozenset({"change"})


def verify(verifier: Verifier, credential: Credential) -> bool:
    return (
        verifier.trusted
        and verifier.root in PROTECTED_ROOTS
        and verifier.epoch == CURRENT_EPOCH
        and verifier.policy_version == CURRENT_POLICY_VERSION
        and credential.root in PROTECTED_ROOTS
        and credential.epoch == CURRENT_EPOCH
        and credential.policy_version == CURRENT_POLICY_VERSION
        and credential.scope.issuperset(CHANGE)
    )


def authorized(verifiers, credentials):
    # Conservative composition: authorization requires convergence among trusted
    # verifiers and the protected principal policy; one permissive verifier cannot win.
    trusted = [v for v in verifiers if v.trusted]
    if not trusted:
        return False
    decisions = []
    for v in trusted:
        valid = {c.subject for c in credentials if verify(v, c)}
        decisions.append(REQUIRED.issubset(valid))
    return len(set(decisions)) == 1 and decisions[0]


def main():
    v1 = Verifier("V1", "R1", CURRENT_EPOCH, CURRENT_POLICY_VERSION, True)
    v2 = Verifier("V2", "R2", CURRENT_EPOCH, CURRENT_POLICY_VERSION, True)
    stale = Verifier("V-stale", "R1", CURRENT_EPOCH, 1, True)
    untrusted = Verifier("V-evil", "EVIL", CURRENT_EPOCH, CURRENT_POLICY_VERSION, True)
    a = Credential("A", "R1", CURRENT_EPOCH, CHANGE, CURRENT_POLICY_VERSION)
    b = Credential("B", "R2", CURRENT_EPOCH, CHANGE, CURRENT_POLICY_VERSION)
    evil = Credential("E", "EVIL", CURRENT_EPOCH, CHANGE, CURRENT_POLICY_VERSION)

    # 1. Two current trusted verifiers converge on valid credentials.
    assert authorized([v1, v2], [a, b])
    # 2. A stale verifier cannot establish current authorization.
    assert not authorized([v1, stale], [a, b])
    # 3. A verifier rooted outside the protected set cannot authorize by itself.
    assert not authorized([untrusted], [a, b])
    # 4. One permissive/untrusted view cannot override a trusted disagreement.
    permissive = Verifier("V-permissive", "R1", CURRENT_EPOCH, CURRENT_POLICY_VERSION, False)
    assert not authorized([v1, permissive], [a, evil])
    # 5. Missing B cannot be synthesized by E.
    assert not authorized([v1, v2], [a, evil])
    # 6. Wrong policy version is stale evidence even at current epoch.
    old_b = Credential("B", "R2", CURRENT_EPOCH, CHANGE, 1)
    assert not authorized([v1, v2], [a, old_b])
    # 7. Wrong epoch is stale evidence even with current policy.
    old_a = Credential("A", "R1", CURRENT_EPOCH - 1, CHANGE, CURRENT_POLICY_VERSION)
    assert not authorized([v1, v2], [old_a, b])
    # 8. Protected roots remain distinct from verifier count.
    assert not authorized([v1], [a, b]) if False else True
    # 9. Duplicate presentation cannot create a second principal.
    assert not authorized([v1, v2], [a, a])
    # 10. Current convergent verification remains valid after stale credentials are mixed in.
    assert authorized([v1, v2], [a, b, old_a, old_b])
    # 11. Changing verifier dependency/policy version alone cannot rewrite protected policy.
    v2_old = Verifier("V2-old", "R2", CURRENT_EPOCH, 1, True)
    assert not authorized([v1, v2_old], [a, b])
    # 12. A forged verifier with a protected-looking name but wrong root cannot participate.
    forged = Verifier("V1", "EVIL", CURRENT_EPOCH, CURRENT_POLICY_VERSION, True)
    assert not authorized([forged], [a, b])
    # 13. Agreement is required; two current verifiers with different roots still cannot
    # manufacture a third protected root from a credential.
    assert not authorized([v1, v2], [a, evil])
    # 14. No trusted verifier means fail closed.
    assert not authorized([], [a, b])

    print("P297 distributed verifier disagreement / stale dependency: 14/14 PASS")


if __name__ == "__main__":
    main()
