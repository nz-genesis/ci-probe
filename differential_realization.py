"""Clean-room differential realization experiment.

One semantic contract is realized by two independent mechanisms. The experiment
compares observable outcomes/evidence without depending on Genesis vocabulary.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class Operation:
    request_id: str
    key: str
    value: str


@dataclass(frozen=True)
class Evidence:
    request_id: str
    mechanism: str
    outcome: str
    observed_value: str | None


class Realizer(Protocol):
    name: str

    def apply(self, operation: Operation, store: dict[str, str]) -> Evidence: ...


class DirectRealizer:
    name = "direct"

    def apply(self, operation: Operation, store: dict[str, str]) -> Evidence:
        store[operation.key] = operation.value
        return Evidence(
            operation.request_id, self.name, "applied", store.get(operation.key)
        )


class QueuedRealizer:
    name = "queued"

    def apply(self, operation: Operation, store: dict[str, str]) -> Evidence:
        queue = [(operation.key, operation.value)]
        while queue:
            key, value = queue.pop(0)
            store[key] = value
        return Evidence(
            operation.request_id, self.name, "applied", store.get(operation.key)
        )


def run_differential() -> tuple[Evidence, Evidence]:
    operation = Operation("req-001", "item", "v1")
    direct_store: dict[str, str] = {}
    queued_store: dict[str, str] = {}

    direct = DirectRealizer().apply(operation, direct_store)
    queued = QueuedRealizer().apply(operation, queued_store)

    assert direct.outcome == queued.outcome == "applied"
    assert direct.observed_value == queued.observed_value == "v1"
    assert direct.request_id == queued.request_id == operation.request_id
    assert direct_store == queued_store == {"item": "v1"}
    assert direct.mechanism != queued.mechanism
    return direct, queued


if __name__ == "__main__":
    print(run_differential())
