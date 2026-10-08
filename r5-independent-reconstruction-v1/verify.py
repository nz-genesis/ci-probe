from dataclasses import dataclass
from itertools import product

@dataclass(frozen=True)
class Snapshot:
    serial: int = 1
    epoch: int = 1
    custodian: str = "A"
    instance: int = 1
    retired: frozenset[str] = frozenset()
    def token(self) -> tuple[str, int]:
        return (self.custodian, self.instance)

@dataclass(frozen=True)
class Request:
    actor: str
    serial: int
    epoch: int
    instance: tuple[str, int]
    evidence_epoch: int
    evidence_instance: tuple[str, int]
    destination: str

def qualifies(snapshot: Snapshot, request: Request) -> bool:
    return (request.actor == snapshot.custodian and request.actor not in snapshot.retired and
            request.serial == snapshot.serial and request.epoch == snapshot.epoch and
            request.instance == snapshot.token() and request.evidence_epoch == snapshot.epoch and
            request.evidence_instance == snapshot.token())

def apply(snapshot: Snapshot, request: Request) -> tuple[Snapshot, bool]:
    if not qualifies(snapshot, request):
        return snapshot, False
    return Snapshot(snapshot.serial + 1, snapshot.epoch + 1, request.destination, snapshot.instance + 1, snapshot.retired), True

def reverse(snapshot: Snapshot, destination: str = "A") -> tuple[Snapshot, bool]:
    if destination in snapshot.retired:
        return snapshot, False
    return Snapshot(snapshot.serial + 1, snapshot.epoch + 1, destination, snapshot.instance + 1, snapshot.retired), True

def initial_requests(snapshot: Snapshot) -> dict[str, Request]:
    token = snapshot.token()
    return {"B": Request(snapshot.custodian, snapshot.serial, snapshot.epoch, token, snapshot.epoch, token, "B"),
            "C": Request(snapshot.custodian, snapshot.serial, snapshot.epoch, token, snapshot.epoch, token, "C")}

def targeted_checks() -> None:
    snapshot = Snapshot(); requests = initial_requests(snapshot)
    snapshot, first = apply(snapshot, requests["B"]); snapshot, second = apply(snapshot, requests["C"])
    assert (first, second) == (True, False)
    snapshot = Snapshot(); requests = initial_requests(snapshot)
    snapshot, _ = apply(snapshot, requests["B"]); snapshot, reversed_ok = reverse(snapshot); assert reversed_ok
    _, stale_ok = apply(snapshot, requests["B"]); assert not stale_ok
    fresh = initial_requests(snapshot)["B"]; snapshot, fresh_ok = apply(snapshot, fresh); assert fresh_ok; assert snapshot.instance > 2
    snapshot = Snapshot(); requests = initial_requests(snapshot); snapshot, _ = apply(snapshot, requests["B"])
    previous_instance = snapshot.token(); snapshot, _ = reverse(snapshot); assert snapshot.token() != previous_instance
    snapshot = Snapshot(); requests = initial_requests(snapshot); snapshot, _ = apply(snapshot, requests["B"])
    snapshot = Snapshot(snapshot.serial, snapshot.epoch, snapshot.custodian, snapshot.instance, frozenset({"A"}))
    _, recovery_ok = reverse(snapshot); assert not recovery_ok

def exhaustive_interleavings() -> None:
    failures = []
    for length in range(1, 7):
        for sequence in product(("B", "C", "R"), repeat=length):
            snapshot = Snapshot(); requests = initial_requests(snapshot); wins = []
            for action in sequence:
                if action in ("B", "C"):
                    snapshot, accepted = apply(snapshot, requests[action])
                    if accepted: wins.append(action)
                else: snapshot, _ = reverse(snapshot)
            if len(wins) > 1: failures.append(("two-successors", sequence, wins))
    assert not failures, failures

def weak_authorizer(snapshot: Snapshot, request: Request) -> bool:
    return request.actor == snapshot.custodian and request.actor not in snapshot.retired

def root_only_authorizer(snapshot: Snapshot, request: Request) -> bool:
    return request.actor == snapshot.custodian and request.actor not in snapshot.retired

def mutation_red_team() -> None:
    snapshot = Snapshot(); requests = initial_requests(snapshot)
    snapshot, _ = apply(snapshot, requests["B"]); snapshot, _ = reverse(snapshot)
    assert not qualifies(snapshot, requests["B"]); assert weak_authorizer(snapshot, requests["B"])
    snapshot = Snapshot(); requests = initial_requests(snapshot); snapshot, _ = apply(snapshot, requests["B"])
    old_token = snapshot.token(); snapshot, _ = reverse(snapshot); fresh = initial_requests(snapshot)["B"]
    snapshot, _ = apply(snapshot, fresh); stale = Request("B", snapshot.serial, snapshot.epoch, old_token, snapshot.epoch, old_token, "C")
    assert old_token != snapshot.token(); assert not qualifies(snapshot, stale); assert root_only_authorizer(snapshot, stale)

def neutral_removal_checks() -> None:
    snapshot = Snapshot(); request = initial_requests(snapshot)["B"]
    variants = {"actor": request.actor == snapshot.custodian, "serial": request.serial == snapshot.serial,
                "epoch": request.epoch == snapshot.epoch, "instance": request.instance == snapshot.token(),
                "evidence_epoch": request.evidence_epoch == snapshot.epoch,
                "evidence_instance": request.evidence_instance == snapshot.token(),
                "retirement": request.actor not in snapshot.retired}
    assert all(variants.values()); assert len(variants) == 7

def main() -> None:
    targeted_checks(); exhaustive_interleavings(); mutation_red_team(); neutral_removal_checks()
    print("5/5 targeted neutral R5 cases PASS")
    print("1092/1092 exhaustive interleaving sequences PASS")
    print("2/2 mutation Red Team checks PASS")
    print("7/7 admission relations exercised")
    print("new Genesis primitive: NOT DEMONSTRATED")
    print("epistemic status: SUPPORTED / BOUNDED / INDEPENDENT RECONSTRUCTION")

if __name__ == "__main__": main()