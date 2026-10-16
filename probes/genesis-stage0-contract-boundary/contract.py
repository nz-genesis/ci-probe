#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
from typing import Any


class Status(str, Enum):
    ADMISSIBLE = "ADMISSIBLE"
    REJECTED = "REJECTED"
    UNKNOWN = "UNKNOWN"
    FAILED = "FAILED"


@dataclass(frozen=True)
class State:
    scope: str
    version: int
    digest: str


@dataclass(frozen=True)
class Capability:
    name: str
    parameters: dict[str, Any]


@dataclass(frozen=True)
class Authority:
    subject: str
    scope: str
    action: str


@dataclass(frozen=True)
class Constraint:
    name: str
    value: Any


@dataclass(frozen=True)
class ExecutableContract:
    transition: str
    state: State
    capability: Capability
    authority: Authority
    constraints: tuple[Constraint, ...]
    payload: dict[str, Any]


@dataclass(frozen=True)
class Observation:
    status: Status
    state_before: State
    state_after: State | None
    effect: dict[str, Any]


@dataclass(frozen=True)
class Evidence:
    observation: Observation
    source: str
    verifier: str
    limitations: tuple[str, ...]


def _plain(value: Any) -> Any:
    if hasattr(value, "__dataclass_fields__"):
        return {k: _plain(getattr(value, k)) for k in value.__dataclass_fields__}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, tuple):
        return [_plain(x) for x in value]
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    return value


def canonical_bytes(contract: ExecutableContract) -> bytes:
    return json.dumps(
        _plain(contract), sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def contract_sha256(contract: ExecutableContract) -> str:
    return hashlib.sha256(canonical_bytes(contract)).hexdigest()


def check_capability(contract: ExecutableContract, available: set[str]) -> Status:
    if contract.capability.name in available:
        return Status.ADMISSIBLE
    return Status.REJECTED


def check_authority(contract: ExecutableContract, permitted: set[tuple[str, str, str]]) -> Status:
    key = (contract.authority.subject, contract.authority.scope, contract.authority.action)
    if key in permitted:
        return Status.ADMISSIBLE
    return Status.REJECTED


def check_constraints(contract: ExecutableContract, known: dict[str, Any]) -> Status:
    for constraint in contract.constraints:
        if constraint.name not in known:
            return Status.UNKNOWN
        if known[constraint.name] != constraint.value:
            return Status.REJECTED
    return Status.ADMISSIBLE


def admit(
    contract: ExecutableContract,
    *,
    available_capabilities: set[str],
    permitted_authorities: set[tuple[str, str, str]],
    known_constraints: dict[str, Any],
) -> Status:
    capability = check_capability(contract, available_capabilities)
    if capability is not Status.ADMISSIBLE:
        return capability
    authority = check_authority(contract, permitted_authorities)
    if authority is not Status.ADMISSIBLE:
        return authority
    return check_constraints(contract, known_constraints)
