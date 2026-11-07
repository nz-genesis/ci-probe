"""Generic, side-effect-free execution semantics probe."""
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
    idempotency_key: str = ""


@dataclass
class ExecutionRecord:
    action_id: str
    target: str = ""
    operation: str = ""
    required_capability: str = ""
    authority: str = ""
    status: Status = Status.CANDIDATE
    attempts: int = 0
    observed: Mapping[str, Any] = field(default_factory=dict)
    outcome: Mapping[str, Any] = field(default_factory=dict)
    observation_recorded: bool = False
    reconciled: bool = False
    trace: list[str] = field(default_factory=list)


class AdmissionError(Exception):
    pass


class DuplicateExecutionError(Exception):
    pass


class ScopeViolationError(Exception):
    pass


class AuthorizationRevokedError(Exception):
    pass


class CapabilityRevokedError(Exception):
    pass


def admit(contract: ActionContract, *, capabilities: set[str], authorities: set[str]) -> ExecutionRecord:
    if not contract.target or not contract.operation:
        raise AdmissionError("target and operation are required")
    if not contract.required_capability:
        raise AdmissionError("required capability is required")
    if not contract.authority:
        raise AdmissionError("authority is required")
    if contract.required_capability not in capabilities:
        raise AdmissionError("required capability is unavailable")
    if contract.authority not in authorities:
        raise AdmissionError("required authority is unavailable")
    record = ExecutionRecord(
        action_id=f"{contract.target}:{contract.operation}",
        target=contract.target,
        operation=contract.operation,
        required_capability=contract.required_capability,
        authority=contract.authority,
    )
    record.status = Status.ADMITTED
    record.trace.append("admitted")
    return record


def execute_once(
    record: ExecutionRecord,
    *,
    effect: Mapping[str, Any],
    target: str,
    operation: str,
    active_capabilities: set[str],
    active_authorities: set[str],
    acknowledgement_lost: bool = False,
) -> ExecutionRecord:
    if record.status != Status.ADMITTED:
        raise AdmissionError(f"cannot execute from status={record.status.value}")
    if record.attempts:
        raise DuplicateExecutionError("execution already attempted; reconcile before retry")
    if target != record.target:
        raise ScopeViolationError("executor target is outside admitted scope")
    if operation != record.operation:
        raise ScopeViolationError("executor operation is outside admitted scope")
    if record.required_capability not in active_capabilities:
        raise CapabilityRevokedError("required capability is no longer active")
    if record.authority not in active_authorities:
        raise AuthorizationRevokedError("execution authority is no longer active")
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
    if record.status != Status.COMPLETED or record.attempts != 1:
        raise AdmissionError("direct observation requires one completed execution attempt")
    record.observed = dict(observed)
    record.observation_recorded = True
    record.trace.append("observed")
    return record


def verify(record: ExecutionRecord, expected: Mapping[str, Any]) -> ExecutionRecord:
    if record.attempts != 1 or record.status not in {Status.COMPLETED, Status.UNKNOWN}:
        raise AdmissionError(f"cannot verify from status={record.status.value}")
    if not record.observation_recorded:
        raise AdmissionError("verification requires an explicit observation")
    if record.status == Status.UNKNOWN and not record.reconciled:
        raise AdmissionError("unknown execution must be reconciled before verification")
    record.status = Status.VERIFIED if record.observed == dict(expected) else Status.VERIFICATION_FAILED
    record.trace.append(record.status.value)
    return record


def reconcile(record: ExecutionRecord, observed: Mapping[str, Any]) -> ExecutionRecord:
    if record.status != Status.UNKNOWN or record.attempts != 1:
        raise AdmissionError("reconciliation requires an unknown state after one execution attempt")
    record.observed = dict(observed)
    record.observation_recorded = True
    record.reconciled = True
    record.trace.append("reconciled")
    return record


def safe_retry(record: ExecutionRecord) -> bool:
    """True only while the same record remains eligible for its first dispatch."""
    return record.status == Status.ADMITTED and record.attempts == 0
