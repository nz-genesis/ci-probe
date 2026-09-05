"""P307 bounded executable model: provider contract x governed retry/recovery cost."""
from itertools import product

CONTRACTS = ("NON_IDEMPOTENT", "IDEMPOTENT", "RECONCILIABLE")
FIRST = ("APPLIED_UNKNOWN", "NOT_APPLIED_UNKNOWN", "REJECTED", "APPLIED")
RECON = (False, True)
CURRENT = (True, False)


def retry_allowed(contract, first, reconciled, current):
    if not current or first in ("REJECTED", "APPLIED"):
        return False
    if contract == "IDEMPOTENT":
        return True
    if contract == "RECONCILIABLE":
        return first == "NOT_APPLIED_UNKNOWN" and reconciled
    return False


def main():
    checked = unsafe = 0
    attempts = {c: 0 for c in CONTRACTS}
    for contract, first, reconciled, current in product(CONTRACTS, FIRST, RECON, CURRENT):
        checked += 1
        allowed = retry_allowed(contract, first, reconciled, current)
        if allowed:
            attempts[contract] += 1
        if not current and allowed:
            unsafe += 1
        if contract == "NON_IDEMPOTENT" and allowed:
            unsafe += 1
        if contract == "RECONCILIABLE" and allowed and not (first == "NOT_APPLIED_UNKNOWN" and reconciled):
            unsafe += 1
    assert unsafe == 0
    print(f"P307 provider-contract safety matrix: {checked}/{checked} PASS")
    for c in CONTRACTS:
        print(f"{c}: retry_permissions={attempts[c]}")


if __name__ == "__main__":
    main()
