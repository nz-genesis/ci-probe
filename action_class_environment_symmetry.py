"""Bounded multi-action-class environment symmetry probe.

Clean-room semantic model. It tests whether several materially different action
classes can preserve one Genesis-side contract across distinct realization
boundaries without introducing environment-specific primitives.
"""
from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Contract:
    operation_id: str
    authority: str
    capability: str
    version: int
    payload: object


@dataclass(frozen=True)
class Outcome:
    effect: object
    observed: object
    verified: bool


class Realization:
    name = "abstract"

    def __init__(self):
        self.state = {"value": 0, "artifact": None, "config": "v1"}

    def execute(self, c: Contract) -> Outcome:
        if c.authority != "allow":
            raise PermissionError("authority denied")
        if c.version != 1:
            raise ValueError("stale contract")
        before = dict(self.state)
        if c.capability == "mutate_state":
            self.state["value"] += int(c.payload)
            expected = self.state["value"]
        elif c.capability == "create_artifact":
            self.state["artifact"] = str(c.payload)
            expected = self.state["artifact"]
        elif c.capability == "observe":
            expected = dict(self.state)
        elif c.capability == "protected_change":
            if c.payload != "v2":
                raise ValueError("invalid protected change")
            self.state["config"] = "v2"
            expected = self.state["config"]
        else:
            raise ValueError("unsupported capability")
        observed = self.observe()
        if c.capability == "observe":
            verified = observed == expected
        elif c.capability == "mutate_state":
            verified = observed["value"] == expected
        elif c.capability == "create_artifact":
            verified = observed["artifact"] == expected
        else:
            verified = observed["config"] == expected
        return Outcome(effect=expected, observed=observed, verified=verified)

    def observe(self):
        return dict(self.state)


class OwnState(Realization): name = "own_state"
class LocalProcess(Realization): name = "local_process"
class FileStorage(Realization): name = "filesystem_storage"
class AttachedHardware(Realization): name = "attached_hardware"
class LocalNetwork(Realization): name = "local_network"
class RemoteSystem(Realization): name = "remote_system"
class AnotherGenesis(Realization): name = "another_genesis"
class Internet(Realization): name = "internet"
class Human(Realization): name = "human"
class PhysicalEnvironment(Realization): name = "physical_environment"
class SimulatedEnvironment(Realization): name = "simulated_environment"

ENVIRONMENTS = [OwnState, LocalProcess, FileStorage, AttachedHardware, LocalNetwork,
                RemoteSystem, AnotherGenesis, Internet, Human, PhysicalEnvironment,
                SimulatedEnvironment]

CASES = [
    ("mutate_state", 5, lambda o: o.observed["value"] == 5),
    ("create_artifact", "artifact-α", lambda o: o.observed["artifact"] == "artifact-α"),
    ("observe", None, lambda o: o.verified and o.observed["value"] == 0),
    ("protected_change", "v2", lambda o: o.observed["config"] == "v2"),
]


def run_case(capability, payload, predicate, env_type):
    env = env_type()
    c = Contract(f"{capability}-1", "allow", capability, 1, payload)
    out = env.execute(c)
    assert out.verified and predicate(out), f"verification failed: {env.name}/{capability}"
    try:
        env.execute(replace(c, authority="deny", operation_id="deny"))
    except PermissionError:
        pass
    else:
        raise AssertionError(f"authority bypass: {env.name}/{capability}")
    try:
        env.execute(replace(c, version=0, operation_id="stale"))
    except ValueError:
        pass
    else:
        raise AssertionError(f"stale contract accepted: {env.name}/{capability}")
    return out


def main():
    count = 0
    for capability, payload, predicate in CASES:
        for env_type in ENVIRONMENTS:
            run_case(capability, payload, predicate, env_type)
            count += 1
    assert count == 44
    print(f"MULTI-ACTION ENVIRONMENT SYMMETRY: {count}/44 PASS")
    print("Four action classes × eleven realization classes; no environment field in the contract.")


if __name__ == "__main__":
    main()
