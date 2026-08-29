"""Clean-room dynamic delegation and revocation experiment.

Two-hop authority is modeled as data. A proposal is valid only when the entire
active delegation chain is valid at the realization boundary. A stale-chain
mechanism is compared with boundary revalidation.
"""

from dataclasses import dataclass
from enum import Enum


class Mechanism(str, Enum):
    STALE_CHAIN = "stale-delegation-chain"
    REVALIDATE_CHAIN = "revalidate-delegation-chain"


class Outcome(str, Enum):
    EXECUTED = "executed"
    BLOCKED_REVOKED = "blocked-revoked"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class Delegation:
    delegator: str
    delegatee: str
    valid_at_request: bool
    valid_at_realization: bool


@dataclass(frozen=True)
class Proposal:
    request_id: str
    irreversible: bool
    human_approved: bool
    root_to_agent: Delegation
    agent_to_executor: Delegation
    acknowledgement: bool
    effect_observed: bool


def chain_valid_at_realization(proposal: Proposal) -> bool:
    return (
        proposal.root_to_agent.valid_at_realization
        and proposal.agent_to_executor.valid_at_realization
    )


def realize(proposal: Proposal, mechanism: Mechanism) -> Outcome:
    if not proposal.human_approved:
        return Outcome.BLOCKED_REVOKED

    if mechanism is Mechanism.REVALIDATE_CHAIN:
        if not chain_valid_at_realization(proposal):
            return Outcome.BLOCKED_REVOKED
    else:
        if not (
            proposal.root_to_agent.valid_at_request
            and proposal.agent_to_executor.valid_at_request
        ):
            return Outcome.BLOCKED_REVOKED

    if not proposal.acknowledgement and not proposal.effect_observed:
        return Outcome.UNKNOWN
    return Outcome.EXECUTED


STABLE = Proposal(
    "req-101",
    True,
    True,
    Delegation("root", "agent", True, True),
    Delegation("agent", "executor", True, True),
    True,
    True,
)

ROOT_REVOKES_AGENT = Proposal(
    "req-102",
    True,
    True,
    Delegation("root", "agent", True, False),
    Delegation("agent", "executor", True, True),
    True,
    False,
)

EXECUTOR_DELEGATION_REVOKED = Proposal(
    "req-103",
    True,
    True,
    Delegation("root", "agent", True, True),
    Delegation("agent", "executor", True, False),
    True,
    False,
)

LATE_EVIDENCE = Proposal(
    "req-104",
    True,
    True,
    Delegation("root", "agent", True, True),
    Delegation("agent", "executor", True, True),
    False,
    False,
)


def verify() -> None:
    assert realize(STABLE, Mechanism.STALE_CHAIN) == Outcome.EXECUTED
    assert realize(STABLE, Mechanism.REVALIDATE_CHAIN) == Outcome.EXECUTED

    assert realize(ROOT_REVOKES_AGENT, Mechanism.STALE_CHAIN) == Outcome.EXECUTED
    assert realize(ROOT_REVOKES_AGENT, Mechanism.REVALIDATE_CHAIN) == Outcome.BLOCKED_REVOKED

    assert realize(EXECUTOR_DELEGATION_REVOKED, Mechanism.STALE_CHAIN) == Outcome.EXECUTED
    assert realize(EXECUTOR_DELEGATION_REVOKED, Mechanism.REVALIDATE_CHAIN) == Outcome.BLOCKED_REVOKED

    assert realize(LATE_EVIDENCE, Mechanism.REVALIDATE_CHAIN) == Outcome.UNKNOWN


if __name__ == "__main__":
    verify()
    print("dynamic delegation: PASS")
