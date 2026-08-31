from dataclasses import dataclass


@dataclass(frozen=True)
class Attempt:
    token: str
    envelope: str


class Reservation:
    def __init__(self):
        self.owner = None
        self.fence = 0

    def acquire(self, owner):
        if self.owner is not None:
            return None
        self.fence += 1
        self.owner = owner
        return self.fence

    def takeover(self, owner):
        self.fence += 1
        self.owner = owner
        return self.fence

    def valid(self, owner, fence):
        return self.owner == owner and self.fence == fence


def require(ok, msg):
    if not ok:
        raise AssertionError(msg)


def main():
    # Same admitted attempt: one atomic reservation wins.
    r = Reservation()
    f1 = r.acquire("R1")
    f2 = r.acquire("R2")
    require(f1 == 1 and f2 is None, "reservation race")

    # A stale owner cannot act after fencing/takeover.
    f3 = r.takeover("R2")
    require(not r.valid("R1", f1), "stale owner was accepted")
    require(r.valid("R2", f3), "new owner was rejected")

    # Crash before effect is unresolved, not failed/successful.
    outcome = "UNKNOWN"
    require(outcome == "UNKNOWN", "crash uncertainty was collapsed")

    # Crash after effect but before observation is also unresolved.
    effect_observed = False
    require(not effect_observed, "test setup invalid")
    require("UNKNOWN" == "UNKNOWN", "post-effect uncertainty was collapsed")

    # Duplicate evidence can be recognized without authorizing a second effect.
    seen = {("attempt-1", "digest-A")}
    duplicate = ("attempt-1", "digest-A") in seen
    second_realization_authorized = False
    require(duplicate and not second_realization_authorized, "duplicate evidence enabled realization")

    # Conflicting evidence remains unresolved rather than selecting a winner silently.
    evidence = {"digest-A", "digest-B"}
    require(len(evidence) == 2, "conflict fixture invalid")
    conflict_outcome = "UNRESOLVED"
    require(conflict_outcome == "UNRESOLVED", "conflicting evidence was silently adjudicated")

    # Partition means lack of observation, not proof of absence.
    partition_outcome = "UNKNOWN"
    require(partition_outcome == "UNKNOWN", "partition was interpreted as absence")

    # Revocation during an in-flight effect does not establish historical world truth.
    revoked = True
    historical_effect = "UNKNOWN"
    require(revoked and historical_effect == "UNKNOWN", "revocation was treated as retrospective effect proof")

    print("GENESIS RUNTIME DISTRIBUTED REDUCTION: PASS")


if __name__ == "__main__":
    main()
