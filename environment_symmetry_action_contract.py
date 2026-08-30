"""Bounded environment-symmetry probe for Genesis Base.

This is a semantic clean-room model, not a claim of real-world integration.
It tests whether one action contract can cross materially different realization
boundaries without adding environment-specific Genesis primitives.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Action:
    operation_id: str
    principal: str
    authority: str
    capability: str
    contract_version: int
    delta: int


@dataclass(frozen=True)
class Result:
    environment: str
    before: int
    after: int
    observed: int
    verified: bool


class Realization:
    name = "abstract"

    def __init__(self):
        self.value = 0
        self.version = 1

    def execute(self, action: Action) -> Result:
        if action.authority != "allow":
            raise PermissionError("authority denied")
        if action.contract_version != self.version:
            raise ValueError("stale contract version")
        if action.capability != "increment":
            raise ValueError("unsupported capability")
        before = self.value
        self.value += action.delta
        observed = self.observe()
        verified = observed == before + action.delta
        return Result(self.name, before, self.value, observed, verified)

    def observe(self) -> int:
        return self.value


class OwnState(Realization):
    name = "own_state"


class LocalProcess(Realization):
    name = "local_process"


class FileStorage(Realization):
    name = "filesystem_storage"


class AttachedHardware(Realization):
    name = "attached_hardware"


class LocalNetwork(Realization):
    name = "local_network"


class RemoteSystem(Realization):
    name = "remote_system"


class AnotherGenesis(Realization):
    name = "another_genesis"


class Internet(Realization):
    name = "internet"


class Human(Realization):
    name = "human"


class PhysicalEnvironment(Realization):
    name = "physical_environment"


class SimulatedEnvironment(Realization):
    name = "simulated_environment"


ENVIRONMENTS = [
    OwnState, LocalProcess, FileStorage, AttachedHardware, LocalNetwork,
    RemoteSystem, AnotherGenesis, Internet, Human, PhysicalEnvironment,
    SimulatedEnvironment,
]


def main() -> None:
    action = Action("op-1", "principal-1", "allow", "increment", 1, 3)
    results = []

    # Same action contract; only realization class changes.
    for env_type in ENVIRONMENTS:
        env = env_type()
        result = env.execute(action)
        assert result.before == 0
        assert result.after == 3
        assert result.observed == 3
        assert result.verified is True
        results.append(result)

        # Authority remains a Genesis-side admission invariant.
        try:
            env.execute(Action("op-deny", "principal-1", "deny", "increment", 1, 3))
        except PermissionError:
            pass
        else:
            raise AssertionError(f"authority bypass: {env.name}")

        # Contract version remains independent of environment.
        try:
            env.execute(Action("op-stale", "principal-1", "allow", "increment", 0, 3))
        except ValueError:
            pass
        else:
            raise AssertionError(f"stale contract accepted: {env.name}")

    assert len({r.after for r in results}) == 1
    assert all(r.verified for r in results)
    print(f"ENVIRONMENT SYMMETRY: {len(results)}/{len(ENVIRONMENTS)} PASS")
    print("Invariant: one action contract -> realization -> observation -> verification")
    print("No environment-specific Genesis primitive is introduced.")


if __name__ == "__main__":
    main()
