"""Executable checks for dynamic delegation."""

from dynamic_delegation import (
    Mechanism,
    Outcome,
    EXECUTOR_DELEGATION_REVOKED,
    LATE_EVIDENCE,
    ROOT_REVOKES_AGENT,
    STABLE,
    realize,
    verify,
)


def test_experiment_invariants() -> None:
    verify()


def test_revocation_at_each_delegation_edge_blocks_revalidated_realization() -> None:
    assert realize(ROOT_REVOKES_AGENT, Mechanism.REVALIDATE_CHAIN) == Outcome.BLOCKED_REVOKED
    assert realize(EXECUTOR_DELEGATION_REVOKED, Mechanism.REVALIDATE_CHAIN) == Outcome.BLOCKED_REVOKED


def test_stale_chain_is_not_semantically_equivalent() -> None:
    assert realize(ROOT_REVOKES_AGENT, Mechanism.STALE_CHAIN) == Outcome.EXECUTED
    assert realize(ROOT_REVOKES_AGENT, Mechanism.REVALIDATE_CHAIN) == Outcome.BLOCKED_REVOKED


def test_late_evidence_remains_unknown() -> None:
    assert realize(LATE_EVIDENCE, Mechanism.REVALIDATE_CHAIN) == Outcome.UNKNOWN


def test_stable_chain_remains_mechanism_independent() -> None:
    assert realize(STABLE, Mechanism.STALE_CHAIN) == Outcome.EXECUTED
    assert realize(STABLE, Mechanism.REVALIDATE_CHAIN) == Outcome.EXECUTED


if __name__ == "__main__":
    test_experiment_invariants()
    test_revocation_at_each_delegation_edge_blocks_revalidated_realization()
    test_stale_chain_is_not_semantically_equivalent()
    test_late_evidence_remains_unknown()
    test_stable_chain_remains_mechanism_independent()
    print("dynamic delegation: PASS")
