"""Clean-room recovery/evidence semantics experiment.

Generic executable experiment only. It deliberately separates acknowledgement,
external effect, evidence, and verification. It contains no private Genesis
hypotheses, credentials, datasets, endpoints, or canonical decisions.
"""
from dataclasses import dataclass
from enum import Enum

class RealizationState(str, Enum):
    FAILED = "FAILED"
    PARTIAL = "PARTIAL"
    UNKNOWN = "UNKNOWN"
    DUPLICATE = "DUPLICATE"
    STALE = "STALE"
    REVOKED = "REVOKED"
    SUCCEEDED = "SUCCEEDED"

@dataclass(frozen=True)
class Observation:
    acknowledgement: str
    effect: str
    evidence: str
    verification: str
    state: RealizationState

def decide(o: Observation) -> str:
    if o.state is RealizationState.REVOKED:
        return "do-not-realize"
    if o.state is RealizationState.STALE:
        return "reconcile"
    if o.state is RealizationState.DUPLICATE:
        return "do-not-duplicate"
    if o.state is RealizationState.UNKNOWN:
        return "reconcile-not-blind-retry"
    if o.state is RealizationState.PARTIAL:
        return "reconcile-partial-effect"
    if o.state is RealizationState.FAILED:
        return "failed"
    if o.state is RealizationState.SUCCEEDED:
        if o.effect != "observed" or o.verification != "verified":
            return "verification-pending"
        return "verified-success"
    raise AssertionError("unhandled state")

def main() -> None:
    cases = {
        "unknown": Observation("lost", "unknown", "absent", "unknown", RealizationState.UNKNOWN),
        "partial": Observation("ack", "partial", "partial", "unknown", RealizationState.PARTIAL),
        "duplicate": Observation("ack", "observed", "duplicate", "unknown", RealizationState.DUPLICATE),
        "stale": Observation("ack", "unknown", "stale", "unknown", RealizationState.STALE),
        "revoked": Observation("none", "none", "none", "not-run", RealizationState.REVOKED),
        "failed": Observation("ack", "none", "failure", "verified", RealizationState.FAILED),
        "effect_unverified": Observation("ack", "observed", "present", "unknown", RealizationState.SUCCEEDED),
        "verified": Observation("ack", "observed", "present", "verified", RealizationState.SUCCEEDED),
    }
    assert decide(cases["unknown"]) == "reconcile-not-blind-retry"
    assert decide(cases["partial"]) == "reconcile-partial-effect"
    assert decide(cases["duplicate"]) == "do-not-duplicate"
    assert decide(cases["stale"]) == "reconcile"
    assert decide(cases["revoked"]) == "do-not-realize"
    assert decide(cases["failed"]) == "failed"
    assert decide(cases["effect_unverified"]) == "verification-pending"
    assert decide(cases["verified"]) == "verified-success"
    assert decide(cases["unknown"]) != decide(cases["failed"])
    assert decide(cases["unknown"]) != "retry"
    assert decide(cases["effect_unverified"]) != "verified-success"
    print("external realization recovery/evidence semantics: PASS")
    print("states=FAILED,PARTIAL,UNKNOWN,DUPLICATE,STALE,REVOKED,SUCCEEDED")
    print("separation=acknowledgement!=effect!=evidence!=verification")
    print("unknown!=failed; unknown!=blind-retry")

if __name__ == "__main__":
    main()
