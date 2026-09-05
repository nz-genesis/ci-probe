#!/usr/bin/env python3
"""P289 — bounded protected-boundary realization comparison.

This is a comparative model, not a production security proof. It asks which
minimal authority root can keep the qualification boundary outside the
mutable target while preserving autonomy and avoiding duplicated governance
engines.
"""
from dataclasses import dataclass
from enum import Enum

class RootKind(Enum):
    HITL = "hitl-owner"
    CRYPTO = "cryptographic-root"
    DEPLOYMENT = "deployment-root"
    BOOTSTRAP = "immutable-bootstrap"

@dataclass(frozen=True)
class Root:
    kind: RootKind
    external_to_target: bool
    mutable_by_target: bool
    supports_independent_verification: bool
    supports_recovery_rotation: bool
    requires_human_per_transition: bool
    duplicated_engine: bool = False

@dataclass(frozen=True)
class Candidate:
    root: Root
    boundary_id: str
    epoch: int
    authority: str

@dataclass(frozen=True)
class Transition:
    epoch: int
    authority: str
    current_boundary: str
    requested_boundary: str
    consequential: bool


def admits(root: Root, candidate: Candidate, t: Transition) -> bool:
    # The root must remain outside the mutable target and independently
    # constrain the qualification relation. A candidate cannot manufacture
    # or replace its own root/boundary merely by requesting the replacement.
    return (
        root.external_to_target
        and not root.mutable_by_target
        and root.supports_independent_verification
        and not root.duplicated_engine
        and candidate.epoch == t.epoch
        and candidate.authority == t.authority
        and candidate.boundary_id == t.current_boundary
        and t.requested_boundary == t.current_boundary
    )


def cost_score(root: Root) -> int:
    # Lower is better. This is a bounded ordinal model, not an empirical
    # benchmark; it prevents qualitative cost claims from being treated as
    # measured facts.
    return (
        3 * int(root.requires_human_per_transition)
        + 2 * int(root.duplicated_engine)
        + 1 * int(not root.supports_recovery_rotation)
    )


def main() -> None:
    roots = [
        Root(RootKind.HITL, True, False, True, True, True),
        Root(RootKind.CRYPTO, True, False, True, True, False),
        Root(RootKind.DEPLOYMENT, True, False, True, True, False),
        Root(RootKind.BOOTSTRAP, True, False, True, True, False),
    ]

    state = Candidate(roots[1], "B1", 7, "R1")
    current = Transition(7, "R1", "B1", "B1", True)
    replacement = Transition(7, "R1", "B1", "B2", True)

    # 1–4. Each candidate realization can constrain a normal consequential
    # transition without becoming mutable itself.
    for root in roots:
        c = Candidate(root, "B1", 7, "R1")
        assert admits(root, c, current)

    # 5–8. No realization permits the target to self-authorize a boundary
    # replacement through the ordinary qualification path.
    for root in roots:
        c = Candidate(root, "B1", 7, "R1")
        assert not admits(root, c, replacement)

    # 9. A mutable-by-target root is never acceptable.
    mutable_root = Root(RootKind.BOOTSTRAP, True, True, True, True, False)
    assert not admits(mutable_root, Candidate(mutable_root, "B1", 7, "R1"), current)

    # 10. A root internal to the mutable target is never acceptable.
    internal_root = Root(RootKind.BOOTSTRAP, False, False, True, True, False)
    assert not admits(internal_root, Candidate(internal_root, "B1", 7, "R1"), current)

    # 11. A realization that introduces a duplicate governance engine is rejected
    # by the minimality criterion even if it is otherwise protected.
    duplicated = Root(RootKind.DEPLOYMENT, True, False, True, True, False, duplicated_engine=True)
    assert not admits(duplicated, Candidate(duplicated, "B1", 7, "R1"), current)

    # 12. Stale epoch cannot authorize the current transition.
    stale = Candidate(roots[1], "B1", 6, "R1")
    assert not admits(roots[1], stale, current)

    # 13. Changed authority cannot authorize against the current authority binding.
    changed_authority = Candidate(roots[1], "B1", 7, "R2")
    assert not admits(roots[1], changed_authority, current)

    # 14. Cost model is deliberately ordinal and exposes the optimization tradeoff.
    scores = {root.kind: cost_score(root) for root in roots}
    assert scores[RootKind.CRYPTO] == scores[RootKind.DEPLOYMENT] == scores[RootKind.BOOTSTRAP]
    assert scores[RootKind.HITL] > scores[RootKind.CRYPTO]

    # 15. Recovery rotation is a property of the root contract, not a new
    # RecoveryEngine primitive.
    for root in roots:
        assert root.supports_recovery_rotation

    # 16. Human approval can remain an authority realization without being
    # semantically required for every consequential transition in other roots.
    assert roots[0].requires_human_per_transition
    assert not roots[1].requires_human_per_transition

    print("P289 protected boundary realization comparison: 16/16 PASS")
    print("Cost scores are ordinal model values, not measured production costs.")

if __name__ == "__main__":
    main()
