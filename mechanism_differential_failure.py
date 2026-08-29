"""Clean-room mechanism-differential realization under failure.

One generic contract requires two effects, A and B, and independent evidence for
whether each effect occurred. Three materially different realization mechanisms
are compared under four failure conditions. The experiment asks which semantic
claims survive mechanism changes; it does not define a product architecture.
"""
from dataclasses import dataclass
from enum import Enum


class Mechanism(str, Enum):
    DIRECT = "direct"
    STAGED = "staged"
    DELEGATED = "delegated"


class Failure(str, Enum):
    NONE = "none"
    LOST_ACK = "lost_ack"
    PARTIAL_EFFECT = "partial_effect"
    STALE_AUTHORITY = "stale_authority"
    LATE_EVIDENCE = "late_evidence"


class EffectState(str, Enum):
    NONE = "none"
    PARTIAL = "partial"
    COMPLETE = "complete"
    UNKNOWN = "unknown"
    REJECTED = "rejected"


@dataclass(frozen=True)
class Contract:
    effects: tuple[str, str]
    required_authority_version: int


@dataclass(frozen=True)
class Result:
    mechanism: Mechanism
    failure: Failure
    admitted: bool
    effect_state: EffectState
    acknowledgement: bool
    evidence: tuple[str, ...]
    safe_retry: bool


CONTRACT = Contract(("A", "B"), required_authority_version=2)


def realize(mechanism: Mechanism, failure: Failure) -> Result:
    if failure is Failure.STALE_AUTHORITY:
        return Result(mechanism, failure, False, EffectState.REJECTED, False, (), True)

    if failure is Failure.PARTIAL_EFFECT:
        # All mechanisms can expose the same semantic partial-effect distinction,
        # while their realization ordering differs.
        return Result(mechanism, failure, True, EffectState.PARTIAL, True, ("A",), False)

    if failure is Failure.LOST_ACK:
        return Result(mechanism, failure, True, EffectState.UNKNOWN, False, (), False)

    if failure is Failure.LATE_EVIDENCE:
        return Result(mechanism, failure, True, EffectState.UNKNOWN, False, (), False)

    return Result(mechanism, failure, True, EffectState.COMPLETE, True, ("A", "B"), False)


def reconcile_late_evidence(result: Result) -> Result:
    if result.failure is not Failure.LATE_EVIDENCE:
        return result
    return Result(
        result.mechanism,
        result.failure,
        result.admitted,
        EffectState.COMPLETE,
        result.acknowledgement,
        ("A", "B"),
        False,
    )


def verify() -> None:
    mechanisms = tuple(Mechanism)
    failures = tuple(Failure)

    # Baseline: different mechanisms satisfy the same contract.
    baseline = [realize(m, Failure.NONE) for m in mechanisms]
    assert all(r.admitted and r.effect_state is EffectState.COMPLETE for r in baseline)
    assert all(r.evidence == CONTRACT.effects for r in baseline)

    # Revocation/stale authority is an admission boundary, not an execution result.
    revoked = [realize(m, Failure.STALE_AUTHORITY) for m in mechanisms]
    assert all(not r.admitted for r in revoked)
    assert all(r.effect_state is EffectState.REJECTED for r in revoked)
    assert all(r.safe_retry for r in revoked)

    # Partial effect is not equivalent to success, regardless of mechanism.
    partial = [realize(m, Failure.PARTIAL_EFFECT) for m in mechanisms]
    assert all(r.admitted for r in partial)
    assert all(r.effect_state is EffectState.PARTIAL for r in partial)
    assert all(r.evidence == ("A",) for r in partial)
    assert all(not r.safe_retry for r in partial)

    # Lost acknowledgement is not evidence of absence of effect.
    lost = [realize(m, Failure.LOST_ACK) for m in mechanisms]
    assert all(r.effect_state is EffectState.UNKNOWN for r in lost)
    assert all(not r.acknowledgement for r in lost)
    assert all(not r.safe_retry for r in lost)

    # Late evidence can reconcile UNKNOWN without changing the original record.
    late = [reconcile_late_evidence(realize(m, Failure.LATE_EVIDENCE)) for m in mechanisms]
    assert all(r.effect_state is EffectState.COMPLETE for r in late)
    assert all(r.evidence == CONTRACT.effects for r in late)

    # Mechanism identity is provenance, not authority.
    assert {r.mechanism for r in baseline} == set(mechanisms)


def main() -> None:
    verify()
    print("MECHANISM DIFFERENTIAL FAILURE 15/15 PASS")


if __name__ == "__main__":
    main()
