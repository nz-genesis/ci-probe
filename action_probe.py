"""Generic, side-effect-free execution semantics probe.

This module intentionally knows nothing about Genesis. It models only a generic
consequential action lifecycle so the public repository can test execution
semantics without importing private architecture or research assumptions.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping


class Status(str, Enum):
    CANDIDATE = "candidate"
    ADMITTED = "admitted"
    STARTED = "started"
    COMPLETED = "completed"
    VERIFIED = "verified"
    VERIFICATION_FAILED = "verification_failed"
    REJECTED = "rejected"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class ActionContract:
    target: str
    operation: str
    inputs: Mapping[str, Any] = field(default_factory=dict)
    constraints: Mapping[str, Any] = field(default_factory=dict)
    required_capability: str = ""
    authority: str = ""
    expected_outcome: Mapping[str, Any] = field(default_factory=dict)
    verification: Mapping[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionRecord:
    action_id: str
    status: Status = Status.CANDIDATE
    attempts: int = 0
    observed: Mapping[str, Any] = field(default_factory=dict)
    outcome: Mapping[str, Any] = field(default_factory=dict)
    trace: list[str] = field(default_factory=list)


class AdmissionError(Exception):
    pass


class DuplicateExecutionError(Exception):
    pass


def admit(
    contract: ActionContract,
    *,
    capabilities: set[str],
    authorities: set[str],
) -> ExecutionRecord:
    if contract.required_capability not in capabilities:
        raise AdmissionError("required capability is unavailable")
    if contract.authority not in authorities:
        raise AdmissionError("required authority is unavailable")
    if not contract.target or not contract.operation:
        raise AdmissionError("target and operation are required")
    record = ExecutionRecord(action_id=f"{contract.target}:{contract.operation}")
    record.status = Status.ADMITTED
    record.trace.append("admitted")
    return record


def execute_once(
    record: ExecutionRecord,
    *,
    effect: Mapping[str, Any],
    acknowledgement_lost: bool = False,
) -> ExecutionRecord:
    if record.status not in {Status.ADMITTED, Status.UNKNOWN}:
        raise AdmissionError(f"cannot execute from status={record.status.value}")
    if record.attempts:
        raise DuplicateExecutionError("execution already attempted; reconcile before retry")
    record.attempts += 1
    record.status = Status.STARTED
    record.trace.append("started")
    record.outcome = dict(effect)
    record.trace.append("effect-observed-by-executor")
    if acknowledgement_lost:
        record.status = Status.UNKNOWN
        record.trace.append("acknowledgement-lost")
    else:
        record.status = Status.COMPLETED
        record.trace.append("completed")
    return record


def observe(record: ExecutionRecord, observed: Mapping[str, Any]) -> ExecutionRecord:
    record.observed = dict(observed)
    record.trace.append("observed")
    return record


def verify(record: ExecutionRecord, expected: Mapping[str, Any]) -> ExecutionRecord:
    if record.status not in {Status.COMPLETED, Status.UNKNOWN}:
        raise AdmissionError(f"cannot verify from status={record.status.value}")
    record.status = Status.VERIFIED if record.observed == dict(expected) else Status.VERIFICATION_FAILED
    record.trace.append(record.status.value)
    return record


def safe_retry(record: ExecutionRecord) -> bool:
    """Return whether a retry is safe without reconciliation.

    Unknown or already-attempted execution is deliberately unsafe to retry.
    """
    return record.status == Status.ADMITTED and record.attempts == 0
