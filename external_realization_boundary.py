"""Clean-room test for a public realization boundary.

A generic internal request is projected into a public-safe contract. The public
contract is then realized by two independent mechanisms. The test verifies that
projection removes non-public fields and that both realizations preserve the
same observable contract outcome and request identity.
"""

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class PublicContract:
    request_id: str
    operation: str
    key: str
    value: str
    constraint: str


@dataclass(frozen=True)
class Evidence:
    request_id: str
    mechanism: str
    outcome: str
    observed_value: str | None
    contract_digest: str


ALLOWED_FIELDS = {"request_id", "operation", "key", "value", "constraint"}
FORBIDDEN_FIELDS = {"secret", "internal_note", "authority_token", "dataset_ref"}


def project_public(internal_request: dict[str, str]) -> PublicContract:
    assert FORBIDDEN_FIELDS.intersection(internal_request.keys())
    public = {key: internal_request[key] for key in ALLOWED_FIELDS}
    assert FORBIDDEN_FIELDS.isdisjoint(public.keys())
    return PublicContract(**public)


def digest(contract: PublicContract) -> str:
    canonical = "|".join(
        [contract.request_id, contract.operation, contract.key, contract.value, contract.constraint]
    )
    return sha256(canonical.encode("utf-8")).hexdigest()


def realize_direct(contract: PublicContract) -> Evidence:
    store: dict[str, str] = {}
    store[contract.key] = contract.value
    return Evidence(contract.request_id, "direct", "applied", store.get(contract.key), digest(contract))


def realize_queued(contract: PublicContract) -> Evidence:
    store: dict[str, str] = {}
    queue: list[tuple[str, str]] = [(contract.key, contract.value)]
    while queue:
        key, value = queue.pop(0)
        store[key] = value
    return Evidence(contract.request_id, "queued", "applied", store.get(contract.key), digest(contract))


def run_boundary_check() -> tuple[Evidence, Evidence]:
    internal_request = {
        "request_id": "p189-erb-001",
        "operation": "set",
        "key": "fixture",
        "value": "v1",
        "constraint": "deterministic",
        "secret": "must-not-cross-boundary",
        "internal_note": "private implementation detail",
        "authority_token": "not-public",
        "dataset_ref": "internal-only",
    }

    contract = project_public(internal_request)
    direct = realize_direct(contract)
    queued = realize_queued(contract)

    assert direct.outcome == queued.outcome == "applied"
    assert direct.observed_value == queued.observed_value == "v1"
    assert direct.request_id == queued.request_id == contract.request_id
    assert direct.contract_digest == queued.contract_digest == digest(contract)
    assert direct.mechanism != queued.mechanism
    return direct, queued


if __name__ == "__main__":
    direct, queued = run_boundary_check()
    print("external realization boundary: PASS")
    print(f"request_id={direct.request_id}")
    print(f"outcome={direct.outcome}")
    print(f"observed_value={direct.observed_value}")
    print(f"contract_digest={direct.contract_digest}")
    print(f"mechanisms={direct.mechanism},{queued.mechanism}")
