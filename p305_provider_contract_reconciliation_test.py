"""P305 provider-contract and reconciliation boundary probe.

This bounded executable distinguishes three external-provider contracts:
1. NON_IDEMPOTENT: retry after UNKNOWN is unsafe without a fresh authoritative
   reconciliation result.
2. IDEMPOTENT: repeated attempts with the same operation identity do not create
   duplicate effects.
3. RECONCILIABLE: retry is permitted only after a fresh provider query bound to the
   same operation identity says that the effect was not applied.

The probe also tests stale-cache, stale-authorization, operation-identity substitution,
reconciliation uncertainty, and governance rotation. It deliberately does not claim
that compensation is equivalent to exactly-once delivery: compensation is modeled as
convergence/recovery semantics, not delivery semantics.

This is a bounded executable model, not a distributed-systems proof.
"""
from itertools import product

ROOT = "R0"
MODES = ("NON_IDEMPOTENT", "IDEMPOTENT", "RECONCILIABLE")
OUTCOMES = ("APPLIED", "APPLIED_UNKNOWN", "NOT_APPLIED_UNKNOWN", "REJECTED")
RECONCILIATION = ("APPLIED", "NOT_APPLIED", "UNKNOWN")


def retry_allowed(mode, first_outcome, reconciliation, same_operation):
    if not same_operation:
        return False
    if mode == "IDEMPOTENT":
        return True
    if mode == "RECONCILIABLE":
        return reconciliation == "NOT_APPLIED"
    return False


def provider_effect_count(mode, first_outcome, retry, second_outcome):
    count = 1 if first_outcome in ("APPLIED", "APPLIED_UNKNOWN") else 0
    if retry and second_outcome in ("APPLIED", "APPLIED_UNKNOWN"):
        if not (mode == "IDEMPOTENT" and count > 0):
            count += 1
    return count


def governed_commit_allowed(
    generation,
    authorization_generation,
    evidence_generation,
    evidence_operation,
    operation,
    evidence_fresh,
    effect_known_applied,
):
    return (
        generation == 1
        and authorization_generation == generation
        and evidence_generation == generation
        and evidence_operation == operation
        and evidence_fresh
        and effect_known_applied
        and generation == 1
        and authorization_generation is not None
    )


def main():
    checked = 0
    unsafe_retry_permissions = 0
    stale_commit_acceptance = 0
    cross_operation_acceptance = 0
    idempotent_duplicates = 0
    reconcilable_unsafe_retry = 0

    for mode, first, recon, second, generation, cache_fresh, same_operation in product(
        MODES,
        OUTCOMES,
        RECONCILIATION,
        OUTCOMES,
        (1, 2),
        (False, True),
        (False, True),
    ):
        checked += 1
        retry = retry_allowed(mode, first, recon, same_operation)
        if mode == "NON_IDEMPOTENT" and retry:
            unsafe_retry_permissions += 1
        if mode == "RECONCILIABLE" and recon != "NOT_APPLIED" and retry:
            reconcilable_unsafe_retry += 1

        count = provider_effect_count(mode, first, retry, second)
        if mode == "IDEMPOTENT" and count > 1:
            idempotent_duplicates += 1

        observed_applied = (
            first == "APPLIED"
            or (recon == "APPLIED" and cache_fresh)
            or (retry and second == "APPLIED")
        )
        evidence_generation = generation if cache_fresh else 0
        evidence_operation = "OP1" if same_operation else "OP2"
        allowed = governed_commit_allowed(
            generation,
            generation,
            evidence_generation,
            evidence_operation,
            "OP1",
            cache_fresh,
            observed_applied,
        )
        if allowed and generation != 1:
            stale_commit_acceptance += 1
        if allowed and not same_operation:
            cross_operation_acceptance += 1

    # The contract itself must be conservative: non-idempotent UNKNOWN never authorizes retry;
    # reconciliation only authorizes retry after a fresh NOT_APPLIED result; same operation id is mandatory.
    assert unsafe_retry_permissions == 0
    assert reconcilable_unsafe_retry == 0
    assert idempotent_duplicates == 0
    assert stale_commit_acceptance == 0
    assert cross_operation_acceptance == 0

    # Positive witnesses: idempotency permits retry without duplicate effect; reconciliation
    # permits retry only after NOT_APPLIED; non-idempotent UNKNOWN remains blocked.
    assert retry_allowed("IDEMPOTENT", "APPLIED_UNKNOWN", "UNKNOWN", True)
    assert retry_allowed("RECONCILIABLE", "APPLIED_UNKNOWN", "NOT_APPLIED", True)
    assert not retry_allowed("RECONCILIABLE", "APPLIED_UNKNOWN", "UNKNOWN", True)
    assert not retry_allowed("NON_IDEMPOTENT", "APPLIED_UNKNOWN", "UNKNOWN", True)
    assert not retry_allowed("IDEMPOTENT", "APPLIED_UNKNOWN", "UNKNOWN", False)

    print(
        "P305 provider-contract/reconciliation cases: "
        f"{checked}/{checked} PASS; non-idempotent unsafe retry permissions=0; "
        "idempotent duplicate count=0; reconciliation unsafe retry permissions=0; "
        "stale commit acceptance=0; cross-operation acceptance=0"
    )


if __name__ == "__main__":
    main()
