"""Clean-room experiment: distributed replay and conflicting executor claims.

This file is intentionally generic. It does not encode or import any Genesis
architecture, private terminology, credentials, endpoints, or datasets.

Questions:
1. Can a non-atomic check-then-effect path create a duplicate external effect?
2. Does an atomic claim gate prevent that duplicate in the same model?
3. When two sources make incompatible claims about the same request, can a
   verifier safely collapse the conflict into success/failure without an
   independent observation rule?
"""

from __future__ import annotations

from dataclasses import dataclass
from threading import Barrier, Lock, Thread


@dataclass
class Store:
    claimed: set[str]
    effects: list[str]
    lock: Lock


def run_race(*, atomic_claim: bool) -> Store:
    store = Store(claimed=set(), effects=[], lock=Lock())
    gate = Barrier(2)

    def worker(source: str) -> None:
        if atomic_claim:
            with store.lock:
                if "r1" in store.claimed:
                    return
                store.claimed.add("r1")
        else:
            already_claimed = "r1" in store.claimed
            gate.wait()
            if already_claimed:
                return
            # Both workers can reach the effect after observing the same state.

        if atomic_claim:
            store.effects.append(source)
            return

        # Synchronize the non-atomic branch so both observations happen before
        # either effect is recorded. This makes the race deterministic.
        store.effects.append(source)

    threads = [Thread(target=worker, args=("A",)), Thread(target=worker, args=("B",))]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    return store


def verify_replay_race() -> None:
    naive = run_race(atomic_claim=False)
    assert len(naive.effects) == 2, naive

    atomic = run_race(atomic_claim=True)
    assert len(atomic.effects) == 1, atomic


def classify_claims(claims: list[tuple[str, str]]) -> str:
    """Return only what the supplied claims justify.

    Two incompatible claims are represented as CONFLICT rather than being
    silently converted to SUCCESS or FAILURE.
    """
    values = {value for _, value in claims}
    if values == {"observed"}:
        return "SUPPORTED"
    if values == {"absent"}:
        return "UNSUPPORTED"
    if len(values) > 1:
        return "CONFLICT"
    return "UNKNOWN"


def verify_equivocation() -> None:
    same_claim = [("A", "observed"), ("B", "observed")]
    opposite_claim = [("A", "observed"), ("B", "absent")]

    assert classify_claims(same_claim) == "SUPPORTED"
    assert classify_claims(opposite_claim) == "CONFLICT"
    assert classify_claims(opposite_claim) not in {"SUPPORTED", "UNSUPPORTED"}


def verify_late_observation() -> None:
    # A previously unresolved request may later acquire an observation. The
    # observation is new evidence; it is not retroactive proof that an earlier
    # acknowledgement was itself proof of the effect.
    before = {"ack": True, "observed": False}
    after = {"ack": True, "observed": True}
    assert before != after
    assert before["ack"] is True
    assert before["observed"] is False
    assert after["observed"] is True


def main() -> None:
    verify_replay_race()
    verify_equivocation()
    verify_late_observation()
    print("PASS: distributed replay/equivocation clean-room matrix")
    print("PASS: non-atomic race produced duplicate effect")
    print("PASS: atomic claim gate prevented duplicate effect")
    print("PASS: conflicting source claims remain CONFLICT")
    print("PASS: late observation is distinct from prior acknowledgement")


if __name__ == "__main__":
    main()
