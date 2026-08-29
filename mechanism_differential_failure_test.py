from mechanism_differential_failure import (
    CONTRACT,
    EffectState,
    Failure,
    Mechanism,
    realize,
    reconcile_late_evidence,
)


def main() -> None:
    mechanisms = tuple(Mechanism)

    baseline = [realize(m, Failure.NONE) for m in mechanisms]
    assert all(r.admitted and r.effect_state is EffectState.COMPLETE for r in baseline)
    assert all(r.evidence == CONTRACT.effects for r in baseline)

    revoked = [realize(m, Failure.STALE_AUTHORITY) for m in mechanisms]
    assert all(not r.admitted and r.effect_state is EffectState.REJECTED for r in revoked)

    partial = [realize(m, Failure.PARTIAL_EFFECT) for m in mechanisms]
    assert all(r.effect_state is EffectState.PARTIAL for r in partial)
    assert all(r.evidence == ("A",) and not r.safe_retry for r in partial)

    lost = [realize(m, Failure.LOST_ACK) for m in mechanisms]
    assert all(r.effect_state is EffectState.UNKNOWN for r in lost)
    assert all(not r.acknowledgement and not r.safe_retry for r in lost)

    late = [reconcile_late_evidence(realize(m, Failure.LATE_EVIDENCE)) for m in mechanisms]
    assert all(r.effect_state is EffectState.COMPLETE for r in late)
    assert all(r.evidence == CONTRACT.effects for r in late)

    print("MECHANISM DIFFERENTIAL FAILURE REGRESSION 5/5 PASS")


if __name__ == "__main__":
    main()
