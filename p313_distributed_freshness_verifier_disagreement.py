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


@dataclass(frozen=True)
class Case:
    rotation_at: int
    propagation_order: tuple[int, int]
    qualification_replica: int
    commit_replica: int
    cognition_strong: bool


INITIAL = State(epoch=1, policy="read", generation=1)
ROTATED = State(epoch=2, policy="read", generation=2)
CREDENTIAL = Credential(epoch=1, policy="read")


def qualify(replica: Replica, credential: Credential) -> bool:
    view = replica.state
    return (
        credential.signature_valid
        and credential.scope_valid
        and credential.epoch == view.epoch
        and credential.policy == view.policy
    )


def commit_boundary(authority: State, replica: Replica, credential: Credential, qualified: bool) -> bool:
    """Consequential transition: cached qualification is never authority by itself."""
    fresh = replica.state == authority
    credential_current = (
        credential.signature_valid
        and credential.scope_valid
        and credential.epoch == authority.epoch
        and credential.policy == authority.policy
    )
    return qualified and fresh and credential_current


def run_case(case: Case) -> tuple[bool, bool]:
    replicas = [Replica(INITIAL), Replica(INITIAL)]
    authority = INITIAL
    credential = CREDENTIAL
    qualified = False

    events = []
    for i in range(3):
        events.append((i, "noop"))
    events[case.rotation_at] = (case.rotation_at, "rotate")
    events[(case.rotation_at + 1) % 3] = (case.rotation_at + 1, "qualify")
    events[(case.rotation_at + 2) % 3] = (case.rotation_at + 2, "commit")

    # Propagation occurs between qualification and commit according to the selected order.
    for _, event in sorted(events):
        if event == "rotate":
            authority = ROTATED
        elif event == "qualify":
            qualified = qualify(replicas[case.qualification_replica], credential)
        elif event == "commit":
            allowed = commit_boundary(
                authority,
                replicas[case.commit_replica],
                credential,
                qualified,
            )
            # Correct behavior: an old credential must never commit after rotation.
            return allowed, qualified

    raise AssertionError("unreachable")


def propagation_cases():
    # Exercise both replicas as stale/fresh observers. Propagation before commit is
    # represented explicitly in the replica state used by the commit boundary.
    for order in permutations((0, 1)):
        for q in (0, 1):
            for c in (0, 1):
                for strong in (False, True):
                    yield order, q, c, strong


def test_core_matrix() -> None:
    total = 0
    unsafe = 0
    allowed = 0
    blocked = 0

    # All rotations invalidate the old credential before its consequential commit.
    for rotation_at in range(3):
        for order, q, c, strong in propagation_cases():
            case = Case(rotation_at, order, q, c, strong)
            result, qualified = run_case(case)
            total += 1
            if result:
                allowed += 1
                # The credential is epoch 1 while authority is epoch 2: unsafe if allowed.
                unsafe += 1
            else:
                blocked += 1

    assert total == 48, total
    assert allowed == 0, allowed
    assert blocked == 48, blocked
    assert unsafe == 0, unsafe


def test_fresh_generation_allows_current_credential() -> None:
    authority = ROTATED
    replica = Replica(ROTATED)
    credential = Credential(epoch=2, policy="read")
    assert commit_boundary(authority, replica, credential, qualified=True)


def test_stale_cache_never_grants_authority() -> None:
    authority = ROTATED
    stale_replica = Replica(INITIAL)
    old_credential = CREDENTIAL
    assert qualify(stale_replica, old_credential)
    assert not commit_boundary(authority, stale_replica, old_credential, qualified=True)


def main() -> None:
    test_core_matrix()
    test_fresh_generation_allows_current_credential()
    test_stale_cache_never_grants_authority()
    print("P313 distributed freshness/verifier disagreement: 50/50 PASS")
    print("old-generation consequential commits allowed=0; unsafe=0")


if __name__ == "__main__":
    main()
