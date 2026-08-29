"""Clean-room recovery experiment.

A frozen multi-effect request is evaluated under two realization mechanisms and
injected observable conditions. The experiment asks which evidence is sufficient
to classify recovery state without treating an acknowledgement as proof.
"""

from dataclasses import dataclass
from enum import Enum


class Status(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    PARTIAL = "partial"
    UNKNOWN = "unknown"
    DUPLICATE = "duplicate"
    STALE = "stale"
    REVOKED = "revoked"


class Mechanism(str, Enum):
    DIRECT = "direct"
    QUEUED = "queued"


@dataclass(frozen=True)
class Request:
    request_id: str
    keys: tuple[str, str]
    value: str
    version: int


@dataclass(frozen=True)
class Observation:
    request_id: str
    mechanism: Mechanism
    status: Status
    acknowledgement: bool
    observed_values: tuple[str | None, str | None]
    observed_version: int | None
    effect_count: int
    reconciliation_required: bool


@dataclass(frozen=True)
class Fault:
    name: str
    effect_indices: tuple[int, ...]
    acknowledgement: bool
    observed_values: tuple[str | None, str | None]
    observed_version: int | None
    effect_count: int
    status: Status


FAULTS = (
    Fault("success", (0, 1), True, ("v1", "v1"), 1, 2, Status.SUCCESS),
    Fault("failed_before_effect", (), True, ("v0", "v0"), 0, 0, Status.FAILED),
    Fault("partial", (0,), True, ("v1", "v0"), 1, 1, Status.PARTIAL),
    Fault("unknown_ack_lost", (0, 1), False, (None, None), None, 2, Status.UNKNOWN),
    Fault("duplicate_effect", (0, 1), True, ("v1", "v1"), 1, 3, Status.DUPLICATE),
    Fault("stale_version", (), True, ("v0", "v0"), 0, 0, Status.STALE),
    Fault("revoked_before_realization", (), False, (None, None), None, 0, Status.REVOKED),
)


def realize(
    request: Request,
    mechanism: Mechanism,
    fault: Fault,
    store: dict[str, tuple[str, int, int]],
) -> Observation:
    """Apply an injected bounded condition while retaining mechanism provenance."""
    for index in fault.effect_indices:
        key = request.keys[index]
        current = store.get(key)
        count = (current[2] if current else 0) + 1
        store[key] = (request.value, request.version, count)

    observed_values = []
    for index, key in enumerate(request.keys):
        current = store.get(key)
        supplied = fault.observed_values[index]
        if supplied is None and fault.status not in (Status.UNKNOWN, Status.REVOKED):
            supplied = current[0] if current else None
        observed_values.append(supplied)

    return Observation(
        request.request_id,
        mechanism,
        fault.status,
        fault.acknowledgement,
        (observed_values[0], observed_values[1]),
        fault.observed_version,
        fault.effect_count,
        fault.status in (Status.PARTIAL, Status.UNKNOWN, Status.DUPLICATE),
    )


def run_matrix() -> list[tuple[Observation, Observation]]:
    request = Request("req-001", ("item-a", "item-b"), "v1", 1)
    results: list[tuple[Observation, Observation]] = []
    for fault in FAULTS:
        direct = realize(request, Mechanism.DIRECT, fault, {})
        queued = realize(request, Mechanism.QUEUED, fault, {})
        assert direct.status == queued.status == fault.status
        assert direct.request_id == queued.request_id == request.request_id
        assert direct.mechanism != queued.mechanism
        results.append((direct, queued))
    return results


def safe_retry_from_status(status: Status) -> bool:
    """Status alone never authorizes blind retry for recovery-ambiguous cases."""
    return status == Status.FAILED


def verify_invariants() -> None:
    results = run_matrix()
    by_status = {direct.status: (direct, queued) for direct, queued in results}

    success = by_status[Status.SUCCESS][0]
    assert success.acknowledgement is True
    assert success.observed_values == ("v1", "v1")
    assert success.effect_count == 2
    assert success.reconciliation_required is False

    failed = by_status[Status.FAILED][0]
    assert failed.effect_count == 0
    assert safe_retry_from_status(Status.FAILED) is True

    partial = by_status[Status.PARTIAL][0]
    assert partial.observed_values == ("v1", "v0")
    assert partial.effect_count == 1
    assert partial.reconciliation_required is True

    unknown = by_status[Status.UNKNOWN][0]
    assert unknown.acknowledgement is False
    assert unknown.effect_count == 2
    assert unknown.observed_values == (None, None)
    assert unknown.reconciliation_required is True
    assert safe_retry_from_status(Status.UNKNOWN) is False

    duplicate = by_status[Status.DUPLICATE][0]
    assert duplicate.effect_count == 3
    assert duplicate.reconciliation_required is True

    stale = by_status[Status.STALE][0]
    assert stale.status == Status.STALE
    assert stale.reconciliation_required is False

    revoked = by_status[Status.REVOKED][0]
    assert revoked.effect_count == 0
    assert revoked.reconciliation_required is False


if __name__ == "__main__":
    verify_invariants()
    print("recovery matrix: PASS")
