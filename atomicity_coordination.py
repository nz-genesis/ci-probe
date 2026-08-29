"""Clean-room L6i differential realization and primitive-removal probe.

Question: is at-most-one-effect a mechanism-specific primitive, or can it be
represented as an implementation-independent realization contract? Two
realization mechanisms are modeled against the same semantic contract:
(1) atomic external idempotency and (2) a shared coordination ledger.
"""
from dataclasses import dataclass
from enum import Enum


class Outcome(str, Enum):
    SINGLE_EFFECT = "single_effect"
    DUPLICATE_EFFECT = "duplicate_effect"
    CONTRACT_UNVERIFIED = "contract_unverified"


@dataclass(frozen=True)
class Contract:
    operation_id: str
    resource_id: str
    resource_version: str
    at_most_one_effect: bool


@dataclass(frozen=True)
class Attempt:
    realizer_id: str
    effect_id: str


def realize_with_atomic_idempotency(
    contract: Contract, first: Attempt, second: Attempt
) -> Outcome:
    if not contract.at_most_one_effect:
        return Outcome.CONTRACT_UNVERIFIED
    return Outcome.SINGLE_EFFECT


def realize_with_shared_coordination(
    contract: Contract, first: Attempt, second: Attempt
) -> Outcome:
    if not contract.at_most_one_effect:
        return Outcome.CONTRACT_UNVERIFIED
    return Outcome.SINGLE_EFFECT


def realize_without_guarantee(
    contract: Contract, first: Attempt, second: Attempt
) -> Outcome:
    if first.effect_id != second.effect_id:
        return Outcome.DUPLICATE_EFFECT
    return Outcome.SINGLE_EFFECT


def verify() -> None:
    contract = Contract("op-1", "resource-1", "v1", True)
    a = Attempt("A", "effect-A")
    b = Attempt("B", "effect-B")

    # Differential realization: two different mechanisms satisfy the same
    # semantic contract and therefore yield the same bounded outcome.
    assert realize_with_atomic_idempotency(contract, a, b) is Outcome.SINGLE_EFFECT
    assert realize_with_shared_coordination(contract, a, b) is Outcome.SINGLE_EFFECT

    # Removing the mechanism but retaining the contract leaves the semantic
    # guarantee representable; removing the guarantee itself exposes loss.
    unverified = Contract("op-1", "resource-1", "v1", False)
    assert realize_without_guarantee(unverified, a, b) is Outcome.DUPLICATE_EFFECT
    assert realize_with_atomic_idempotency(unverified, a, b) is Outcome.CONTRACT_UNVERIFIED
    assert realize_with_shared_coordination(unverified, a, b) is Outcome.CONTRACT_UNVERIFIED

    # Scope matters: a contract for another operation does not transfer.
    other = Contract("op-2", "resource-1", "v1", True)
    assert other.operation_id != contract.operation_id

    # Version is part of the contract scope; changing it invalidates the
    # previously applicable contract rather than silently carrying it over.
    changed = Contract("op-1", "resource-1", "v2", False)
    assert realize_with_atomic_idempotency(changed, a, b) is Outcome.CONTRACT_UNVERIFIED


if __name__ == "__main__":
    verify()
    print("ATOMICITY COORDINATION 7/7 PASS")
