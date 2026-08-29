"""Clean-room environment-symmetry probe."""
from dataclasses import dataclass
from typing import Dict, List

@dataclass(frozen=True)
class Contract:
    operation: str
    precondition: str
    postcondition: str
    effect_key: str

@dataclass(frozen=True)
class Result:
    environment: str
    admitted: bool
    final_state: Dict[str, int]
    effect_key: str
    verified: bool

CONTRACT = Contract("set value to 1", "value == 0", "value == 1", "value")

class Environment:
    name = "abstract"
    def realize(self, contract: Contract, state: Dict[str, int]) -> Result:
        if state.get(contract.effect_key) != 0:
            return Result(self.name, False, dict(state), contract.effect_key, False)
        next_state = dict(state)
        next_state[contract.effect_key] = 1
        return Result(self.name, True, next_state, contract.effect_key, True)

class LocalProcess(Environment): name = "local-process"
class FileStorage(Environment): name = "filesystem-storage"
class AttachedDevice(Environment): name = "attached-device"
class LocalNetwork(Environment): name = "local-network"
class RemoteSystem(Environment): name = "remote-system"
class AnotherGenesis(Environment): name = "another-genesis"
class Internet(Environment): name = "internet"
class Human(Environment): name = "human"
class PhysicalEnvironment(Environment): name = "physical-environment"
class SimulatedEnvironment(Environment): name = "simulated-environment"

ENVIRONMENTS: List[Environment] = [LocalProcess(), FileStorage(), AttachedDevice(), LocalNetwork(), RemoteSystem(), AnotherGenesis(), Internet(), Human(), PhysicalEnvironment(), SimulatedEnvironment()]

def run() -> List[Result]:
    return [env.realize(CONTRACT, {"value": 0}) for env in ENVIRONMENTS]

def main() -> None:
    results = run()
    assert len(results) == 10
    assert all(r.admitted and r.verified for r in results)
    assert all(r.final_state == {"value": 1} for r in results)
    assert all(r.effect_key == CONTRACT.effect_key for r in results)
    assert len({r.final_state["value"] for r in results}) == 1
    print("ENVIRONMENT SYMMETRY 10/10 PASS")

if __name__ == "__main__":
    main()
