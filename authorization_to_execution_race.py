from dataclasses import dataclass


@dataclass(frozen=True)
class Auth:
    version: int
    active: bool


def authorize(auth: Auth, required_version: int) -> bool:
    return auth.active and auth.version == required_version


def execute(snapshot: Auth, current: Auth, required_version: int) -> str:
    # Authorization is not durable merely because an earlier check passed.
    # The realization boundary must revalidate the current authority state.
    if not authorize(snapshot, required_version):
        return "DENIED"
    if not authorize(current, required_version):
        return "DENIED"
    return "EXECUTED"


def main():
    cases = 0
    initial = Auth(version=1, active=True)

    # Stable authority: check and realization agree.
    assert execute(initial, initial, 1) == "EXECUTED"; cases += 1

    # Revocation after authorization must deny at realization.
    revoked = Auth(version=1, active=False)
    assert execute(initial, revoked, 1) == "DENIED"; cases += 1

    # Version rotation after authorization must deny the old authority.
    rotated = Auth(version=2, active=True)
    assert execute(initial, rotated, 1) == "DENIED"; cases += 1

    # Re-activation under a new version must not resurrect the old grant.
    assert execute(initial, Auth(version=2, active=True), 1) == "DENIED"; cases += 1

    # A revoked snapshot cannot authorize execution even if current state is active.
    revoked_snapshot = Auth(version=1, active=False)
    assert execute(revoked_snapshot, initial, 1) == "DENIED"; cases += 1

    # Current state may narrow between check and execution.
    narrowed = Auth(version=1, active=False)
    assert execute(initial, narrowed, 1) == "DENIED"; cases += 1

    # Revalidation cannot widen authority: wrong required version remains denied.
    assert execute(initial, initial, 2) == "DENIED"; cases += 1

    # Deterministic stable case.
    assert execute(initial, Auth(version=1, active=True), 1) == "EXECUTED"; cases += 1

    print(f"AUTHORIZATION-TO-EXECUTION RACE: {cases}/8 PASS")
    assert cases == 8


if __name__ == "__main__":
    main()
