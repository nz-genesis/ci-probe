"""Regression checks for the generic HITL recovery race model."""

from hitl_recovery_race import Approval, Authority, Case, Effect, Retry, decide_initial, decide_retry


def main() -> None:
    regressions = [
        (Case(Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, True, True, True), "APPROVED", Retry.SAFE),
        (Case(Authority.ACTIVE, Approval.VALID, Effect.PARTIAL, True, True, True), "APPROVED", Retry.UNSAFE),
        (Case(Authority.REVOKED, Approval.VALID, Effect.UNKNOWN, True, True, True), "BLOCK", Retry.BLOCK),
        (Case(Authority.ACTIVE, Approval.STALE, Effect.UNKNOWN, True, True, True), "BLOCK", Retry.UNSAFE),
        (Case(Authority.ACTIVE, Approval.CONFLICTING, Effect.UNKNOWN, True, True, True), "BLOCK", Retry.UNSAFE),
        (Case(Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, True, False, True), "APPROVED", Retry.UNSAFE),
        (Case(Authority.ACTIVE, Approval.NONE, Effect.NONE, False, False, True), "HITL_REQUIRED", Retry.UNSAFE),
        (Case(Authority.ACTIVE, Approval.VALID, Effect.OBSERVED, True, True, True), "APPROVED", Retry.UNSAFE),
    ]
    for case, expected_initial, expected_retry in regressions:
        assert decide_initial(case) == expected_initial
        assert decide_retry(case) is expected_retry
    print(f"HITL RECOVERY RACE REGRESSION {len(regressions)}/{len(regressions)} PASS")


if __name__ == "__main__":
    main()
