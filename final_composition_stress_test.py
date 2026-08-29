"""Regression suite for the final composition stress model."""

from final_composition_stress import Approval, Authority, Case, Decision, Effect, initial_decision, recovery_decision


def main() -> None:
    regressions = [
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, True, True, True, True, True), Decision.APPROVED, Decision.RETRY_SAFE),
        (Case(Authority.ACTIVE, Authority.REVOKED, Approval.VALID, Effect.UNKNOWN, True, True, True, False, True), Decision.BLOCK, Decision.BLOCK),
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.PARTIAL, True, True, True, False, True), Decision.APPROVED, Decision.RETRY_UNSAFE),
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.OBSERVED, True, True, True, False, True), Decision.APPROVED, Decision.RETRY_UNSAFE),
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, False, True, True, True, True), Decision.APPROVED, Decision.RETRY_UNSAFE),
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.STALE, Effect.UNKNOWN, True, True, True, False, True), Decision.BLOCK, Decision.RETRY_UNSAFE),
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.CONFLICTING, Effect.UNKNOWN, True, True, True, False, True), Decision.BLOCK, Decision.RETRY_UNSAFE),
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, True, False, True, False, True), Decision.APPROVED, Decision.RETRY_UNSAFE),
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.VALID, Effect.UNKNOWN, True, True, False, True, True), Decision.APPROVED, Decision.BLOCK),
        (Case(Authority.ACTIVE, Authority.ACTIVE, Approval.NONE, Effect.NONE, False, False, True, False, True), Decision.HITL_REQUIRED, Decision.RETRY_UNSAFE),
    ]
    for case, expected_initial, expected_recovery in regressions:
        assert initial_decision(case) is expected_initial
        assert recovery_decision(case) is expected_recovery
    print(f"FINAL COMPOSITION STRESS REGRESSION {len(regressions)}/{len(regressions)} PASS")


if __name__ == "__main__":
    main()
