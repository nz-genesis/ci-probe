"""P307 bounded executable model: provider contract x governed retry/recovery cost.

This is a bounded model of control work, not a universal performance benchmark.
It compares three provider contracts and two control policies while preserving
current-generation authority and evidence requirements. Costs are abstract work
units so the result is implementation-independent.
"""
from itertools import product

CONTRACTS = ("NON_IDEMPOTENT", "IDEMPOTENT", "RECONCILIABLE")
FIRST = ("APPLIED_UNKNOWN", "NOT_APPLIED_UNKNOWN", "REJECTED", "APPLIED")
RECON = (False, True)
CURRENT = (True, False)
POLICIES = ("CONSERVATIVE", "SUFFICIENT")


def retry_allowed(contract, first, reconciled, current, policy):
    if not current or first in ("REJECTED", "APPLIED"):
        return False
    if contract == "IDEMPOTENT":
        return True
    if contract == "RECONCILIABLE":
        return first == "NOT_APPLIED_UNKNOWN" and reconciled
    return False


def control_cost(contract, first, reconciled, current, policy):
    cost = 1
    if policy == "CONSERVATIVE" and first.endswith("UNKNOWN"):
        cost += 1
    if policy == "SUFFICIENT" and contract == "RECONCILIABLE" and first == "NOT_APPLIED_UNKNOWN":
        cost += 1
    return cost


def main():
    checked = unsafe = 0
    totals = {(p, c): 0 for p in POLICIES for c in CONTRACTS}
    retries = {(p, c): 0 for p in POLICIES for c in CONTRACTS}

    for contract, first, reconciled, current, policy in product(
        CONTRACTS, FIRST, RECON, CURRENT, POLICIES
    ):
        checked += 1
        allowed = retry_allowed(contract, first, reconciled, current, policy)
        totals[(policy, contract)] += control_cost(contract, first, reconciled, current, policy)
        if allowed:
            retries[(policy, contract)] += 1
        if not current and allowed:
            unsafe += 1
        if contract == "NON_IDEMPOTENT" and allowed:
            unsafe += 1
        if contract == "RECONCILIABLE" and allowed and not (first == "NOT_APPLIED_UNKNOWN" and reconciled):
            unsafe += 1

    assert unsafe == 0
    for contract in CONTRACTS:
        assert retries[("SUFFICIENT", contract)] == retries[("CONSERVATIVE", contract)]

    print(f"P307 provider-contract cost matrix: {checked}/{checked} PASS")
    for contract in CONTRACTS:
        conservative = totals[("CONSERVATIVE", contract)]
        sufficient = totals[("SUFFICIENT", contract)]
        permitted = retries[("SUFFICIENT", contract)]
        print(f"{contract}: conservative_cost={conservative}; sufficient_cost={sufficient}; retry_permissions={permitted}")


if __name__ == "__main__":
    main()
