"""P308 bounded executable model: durable reconciliation and multi-node freshness."""
from itertools import product

CONTRACTS = ("NON_IDEMPOTENT", "IDEMPOTENT", "RECONCILIABLE")
OUTCOMES = ("APPLIED_UNKNOWN", "NOT_APPLIED_UNKNOWN", "REJECTED", "APPLIED")
CACHE = ("CURRENT", "STALE")
OBSERVED = ("MATCH", "MISMATCH")
AUTH = ("CURRENT", "ROTATED")
RECON = ("CONFIRMED", "UNCONFIRMED")


def admissible(contract, outcome, cache, observed, auth, recon):
    if auth != "CURRENT" or cache != "CURRENT" or observed != "MATCH":
        return False
    if outcome == "APPLIED":
        return True
    if outcome == "REJECTED":
        return False
    if outcome == "NOT_APPLIED_UNKNOWN" and recon == "CONFIRMED":
        return contract == "RECONCILIABLE"
    return False


def main():
    checked = unsafe = 0
    for args in product(CONTRACTS, OUTCOMES, CACHE, OBSERVED, AUTH, RECON):
        contract, outcome, cache, observed, auth, recon = args
        checked += 1
        allowed = admissible(*args)
        if (cache == "STALE" or observed == "MISMATCH" or auth == "ROTATED" or outcome == "APPLIED_UNKNOWN") and allowed:
            unsafe += 1
        if contract != "RECONCILIABLE" and outcome == "NOT_APPLIED_UNKNOWN" and recon == "CONFIRMED" and allowed:
            unsafe += 1
    assert unsafe == 0
    print(f"P308 durable-reconciliation matrix: {checked}/{checked} PASS")


if __name__ == "__main__":
    main()
