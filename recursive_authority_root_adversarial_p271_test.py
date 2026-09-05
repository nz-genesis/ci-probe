"""P271 bounded adversarial test: authority-root continuity under recursive change.

Question: can recursive self-change, delegation, coordinator replacement, or
verifier substitution manufacture a new authority basis without crossing an
external/constitutional authority boundary?

This is a semantic executable model, not a cryptographic implementation.
"""
from dataclasses import dataclass, replace
from enum import Enum


class Result(Enum):
    ALLOW = "allow"
    BLOCK = "block"
    UNKNOWN = "unknown"
    CONFLICT = "conflict"


@dataclass(frozen=True)
class Root:
    root_id: str
    epoch: int
    fingerprint: str
    owner_approved: bool = True


@dataclass(frozen=True)
class State:
    generation: int
    authority_epoch: int
    verifier_fingerprint: str
    mechanism_version: int
    root: Root


@dataclass(frozen=True)
class Credential:
    root_id: str
    root_epoch: int
    authority_epoch: int
    scope: frozenset[str]
    issuer: str


@dataclass(frozen=True)
class Candidate:
    generation: int
    root_id: str
    root_epoch: int
    authority_epoch: int
    verifier_fingerprint: str
    target: str
    requested_root: Root | None = None
    requested_authority_epoch: int | None = None
    derived_from: Credential | None = None


def initial() -> State:
    return State(0, 1, "verifier-v1", 1, Root("root-0", 1, "root-h1"))


def qualifies(c: Candidate, s: State) -> bool:
    if c.generation != s.generation:
        return False
    if c.root_id != s.root.root_id or c.root_epoch != s.root.epoch:
        return False
    if c.authority_epoch != s.authority_epoch:
        return False
    if c.verifier_fingerprint != s.verifier_fingerprint:
        return False

    if c.target in {"authority", "root", "purpose"}:
        return False

    if c.requested_authority_epoch is not None and c.requested_authority_epoch > s.authority_epoch:
        return False

    if c.requested_root is not None:
        # Root continuity is not a self-authorized transition. Even an
        # owner-approved candidate must cross the explicit external root gate.
        return False

    if c.derived_from is not None:
        d = c.derived_from
        if d.root_id != s.root.root_id or d.root_epoch != s.root.epoch:
            return False
        if d.authority_epoch != s.authority_epoch:
            return False

    return True


def apply_capability(c: Candidate, s: State) -> State:
    assert qualifies(c, s)
    return replace(s, generation=s.generation + 1)


def external_root_rotate(s: State, new_root: Root) -> State:
    assert new_root.owner_approved
    assert new_root.epoch > s.root.epoch
    return replace(
        s,
        generation=s.generation + 1,
        authority_epoch=s.authority_epoch + 1,
        verifier_fingerprint="verifier-v" + str(new_root.epoch),
        root=new_root,
    )


def reconcile_root(
    local_roots: tuple[Root, ...], authoritative: Root | None
) -> Result:
    if authoritative is None:
        return Result.UNKNOWN
    if not local_roots:
        return Result.UNKNOWN
    if any(root.epoch > authoritative.epoch for root in local_roots):
        return Result.CONFLICT
    matching = tuple(
        root for root in local_roots
        if root.root_id == authoritative.root_id
        and root.epoch == authoritative.epoch
        and root.fingerprint == authoritative.fingerprint
    )
    return Result.ALLOW if matching else Result.CONFLICT


def verify() -> None:
    s = initial()

    # 1. Ordinary recursive capability change remains expressible.
    cap = Candidate(0, "root-0", 1, 1, "verifier-v1", "capability")
    s = apply_capability(cap, s)
    assert s.generation == 1

    # 2. The old candidate cannot be replayed after state advancement.
    assert qualifies(cap, s) is False

    # 3. Self-authorized authority escalation is blocked.
    escalation = Candidate(1, "root-0", 1, 1, "verifier-v1", "capability", requested_authority_epoch=2)
    assert qualifies(escalation, s) is False

    # 4. Self-authorized root replacement is blocked even if the proposed root
    # claims owner approval. The approval flag is not itself the root boundary.
    fake_root = Root("root-attacker", 2, "root-attacker-h", True)
    root_swap = Candidate(1, "root-0", 1, 1, "verifier-v1", "capability", requested_root=fake_root)
    assert qualifies(root_swap, s) is False

    # 5. Verifier substitution is blocked by current root-bound fingerprint.
    verifier_swap = Candidate(1, "root-0", 1, 1, "verifier-attacker", "capability")
    assert qualifies(verifier_swap, s) is False

    # 6. A delegated credential cannot launder authority from an older epoch.
    old = Credential("root-0", 1, 1, frozenset({"capability"}), "delegate-A")
    new_root = Root("root-1", 2, "root-h2", True)
    s2 = external_root_rotate(s, new_root)
    delegated_old = Candidate(
        s2.generation, "root-1", 2, 2, "verifier-v2", "capability", derived_from=old
    )
    assert qualifies(delegated_old, s2) is False

    # 7. A fresh credential derived from the current root/authority can be used.
    fresh = Credential("root-1", 2, 2, frozenset({"capability"}), "delegate-B")
    delegated_fresh = Candidate(
        s2.generation, "root-1", 2, 2, "verifier-v2", "capability", derived_from=fresh
    )
    assert qualifies(delegated_fresh, s2) is True

    # 8. Divergent coordinators cannot resolve root authority from local state alone.
    coordinator_a = s2
    coordinator_b = replace(s2, root=Root("root-fork", 2, "fork-h2"))
    assert reconcile_root((coordinator_a.root, coordinator_b.root), None) is Result.UNKNOWN

    # 9. Reconciliation requires an authoritative root observation, not source majority.
    assert reconcile_root((coordinator_a.root, coordinator_b.root), new_root) is Result.ALLOW
    assert reconcile_root((coordinator_b.root,), new_root) is Result.CONFLICT

    # 10. A locally newer fork cannot silently win over the authoritative root.
    newer_fork = Root("root-fork", 3, "fork-h3")
    assert reconcile_root((newer_fork,), new_root) is Result.CONFLICT

    # 11. Root rotation itself is possible only through the external root gate.
    assert s2.root.root_id == "root-1"
    assert s2.root.epoch == 2
    assert s2.authority_epoch == 2

    # 12. Purpose remains outside ordinary recursive target changes.
    purpose = Candidate(s2.generation, "root-1", 2, 2, "verifier-v2", "purpose")
    assert qualifies(purpose, s2) is False

    # 13. The same governed basis handles a new capability after root rotation.
    capability_after_rotation = Candidate(
        s2.generation, "root-1", 2, 2, "verifier-v2", "capability"
    )
    assert qualifies(capability_after_rotation, s2) is True

    print("P271 recursive authority-root adversarial: 13/13 PASS")


if __name__ == "__main__":
    verify()
