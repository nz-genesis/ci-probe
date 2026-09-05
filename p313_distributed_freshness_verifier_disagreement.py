from __future__ import annotations

from dataclasses import dataclass
from itertools import permutations


@dataclass(frozen=True)
class State:
    epoch: int
    policy: str
    generation: int


@dataclass
class Replica:
    state: State


@dataclass(frozen=True)
class Credential:
    epoch: int
    policy: str
    signature_valid: bool = True
    scope_valid: bool = True


INITIAL = State(epoch=1, policy="read", generation=1)
ROTATED = State(epoch=2, policy="write", generation=2)
OLD_CREDENTIAL = Credential(epoch=1, policy="read")
NEW_CREDENTIAL = Credential(epoch=2, policy="write")


def qualify(replica: Replica, credential: Credential) -> bool:
    view = replica.state
    return (
        credential.signature_valid
        and credential.scope_valid
        and credential.epoch == view.epoch
        and credential.policy == view.policy
        and credential.epoch == view.generation
    )


def commit_boundary(
    authority: State,
    replica: Replica,
    credential: Credential,
    qualified: bool,
) -> bool:
    """Consequential transition: cached qualification is never authority by itself."""
    fresh = replica.state == authority
    credential_current = (
        credential.signature_valid
        and credential.scope_valid
        and credential.epoch == authority.epoch
        and credential.policy == authority.policy
    )
    return qualified and fresh and credential_current


def run_schedule(
    order: tuple[str, ...],
    qualification_replica: int,
    commit_replica: int,
    credential: Credential,
) -> tuple[bool, bool, bool]:
    authority = INITIAL
    replicas = [Replica(INITIAL), Replica(INITIAL)]
    qualified = False
    committed = False

    for event in order:
        if event == "rotate":
            authority = ROTATED
        elif event == "prop0":
            replicas[0].state = authority
        elif event == "prop1":
            replicas[1].state = authority
        elif event == "qualify":
            qualified = qualify(replicas[qualification_replica], credential)
        elif event == "commit":
            committed = commit_boundary(
                authority,
                replicas[commit_replica],
                credential,
                qualified,
            )
            return committed, qualified, authority.epoch == credential.epoch
        else:
            raise AssertionError(event)

    raise AssertionError("schedule did not commit")


def all_schedules():
    # Every ordering of rotation, two independent propagation events,
    # qualification and consequential commit is exercised.
    return permutations(("rotate", "prop0", "prop1", "qualify", "commit"))


def test_temporal_matrix() -> None:
    total = 0
    safe_allowed = 0
    blocked = 0
    unsafe = 0
    old_after_rotation = 0

    for order in all_schedules():
        for q in (0, 1):
            for c in (0, 1):
                for credential in (OLD_CREDENTIAL, NEW_CREDENTIAL):
                    allowed, qualified, current = run_schedule(order, q, c, credential)
                    total += 1

                    rotation_index = order.index("rotate")
                    commit_index = order.index("commit")
                    expected_old_allowed = (
                        credential == OLD_CREDENTIAL and commit_index < rotation_index
                    )
                    expected_new_allowed = credential == NEW_CREDENTIAL and commit_index > rotation_index
                    expected_allowed = expected_old_allowed or expected_new_allowed

                    if allowed:
                        if not expected_allowed:
                            unsafe += 1
                        else:
                            safe_allowed += 1
                    else:
                        blocked += 1

                    if (
                        credential == OLD_CREDENTIAL
                        and commit_index > rotation_index
                    ):
                        old_after_rotation += 1
                        assert not allowed, (order, q, c, qualified, current)

    # 120 event orders × 2 qualification replicas × 2 commit replicas × 2 credentials.
    assert total == 960, total
    assert unsafe == 0, unsafe
    assert old_after_rotation == 480, old_after_rotation
    assert safe_allowed > 0
    assert blocked > 0


def test_stale_cache_never_grants_authority() -> None:
    authority = ROTATED
    stale_replica = Replica(INITIAL)
    assert qualify(stale_replica, OLD_CREDENTIAL)
    assert not commit_boundary(authority, stale_replica, OLD_CREDENTIAL, qualified=True)


def test_fresh_current_credential_can_commit() -> None:
    authority = ROTATED
    replica = Replica(ROTATED)
    assert qualify(replica, NEW_CREDENTIAL)
    assert commit_boundary(authority, replica, NEW_CREDENTIAL, qualified=True)


def test_qualification_cache_is_not_authority() -> None:
    authority = INITIAL
    replica = Replica(INITIAL)
    assert qualify(replica, OLD_CREDENTIAL)
    authority = ROTATED
    assert not commit_boundary(authority, replica, OLD_CREDENTIAL, qualified=True)


def main() -> None:
    test_temporal_matrix()
    test_stale_cache_never_grants_authority()
    test_fresh_current_credential_can_commit()
    test_qualification_cache_is_not_authority()
    print("P313 distributed freshness/verifier disagreement: 963/963 PASS")
    print("old-generation commits after rotation blocked=480; unsafe=0")


if __name__ == "__main__":
    main()
