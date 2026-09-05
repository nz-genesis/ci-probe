from dataclasses import dataclass


@dataclass(frozen=True)
class Verifier:
    name: str
    root: str
    epoch: int
    policy_version: int
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
CHANGE = frozenset({"change"})


def verify(v: Verifier, c: Credential) -> bool:
    return (
        v.trusted and v.root in PROTECTED_ROOTS
        and v.epoch == CURRENT_EPOCH
        and v.policy_version == CURRENT_POLICY_VERSION
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
    decisions = [decision(v, credentials) for v in trusted]
    return len(set(decisions)) == 1 and decisions[0]


def main():
    v1 = Verifier("V1", "R1", CURRENT_EPOCH, CURRENT_POLICY_VERSION, PROTECTED_POLICY, True)
    v2 = Verifier("V2", "R2", CURRENT_EPOCH, CURRENT_POLICY_VERSION, PROTECTED_POLICY, True)
    permissive = Verifier("V-permissive", "R1", CURRENT_EPOCH, CURRENT_POLICY_VERSION, frozenset({"A"}), True)
    stale = Verifier("V-stale", "R1", CURRENT_EPOCH, 1, PROTECTED_POLICY, True)
    evil_root = Verifier("V-evil", "EVIL", CURRENT_EPOCH, CURRENT_POLICY_VERSION, PROTECTED_POLICY, True)
    a = Credential("A", "R1", CURRENT_EPOCH, CHANGE, CURRENT_POLICY_VERSION)
    b = Credential("B", "R2", CURRENT_EPOCH, CHANGE, CURRENT_POLICY_VERSION)
    e = Credential("E", "EVIL", CURRENT_EPOCH, CHANGE, CURRENT_POLICY_VERSION)
    old_b = Credential("B", "R2", CURRENT_EPOCH, CHANGE, 1)
    old_a = Credential("A", "R1", CURRENT_EPOCH - 1, CHANGE, CURRENT_POLICY_VERSION)

    assert authorized([v1, v2], [a, b])
    assert not authorized([v1, permissive], [a])
    assert not authorized([v1, permissive], [a, e])
    assert not authorized([v1, stale], [a, b])
    assert not authorized([evil_root], [a, b])
    assert not authorized([v1, v2], [a, e])
    assert not authorized([v1, v2], [a, old_b])
    assert not authorized([v1, v2], [old_a, b])
    assert not authorized([v1, v2], [a, a])
    assert authorized([v1, v2], [a, b, old_a, old_b])
    assert not authorized([v1, permissive], [a, b])
    forged = Verifier("V1", "EVIL", CURRENT_EPOCH, CURRENT_POLICY_VERSION, PROTECTED_POLICY, True)
    assert not authorized([forged], [a, b])
    assert not authorized([v1, v2], [a, e])
    assert not authorized([], [a, b])

    print("P297 distributed verifier disagreement / stale dependency: 14/14 PASS")


if __name__ == "__main__":
    main()
