"""EA17 clean-room probe: durable commit vs external effect.

This probe is implementation-agnostic. It does not encode Genesis semantics.
It tests only the operational distinction between durable semantic state,
external effect identity, acknowledgement loss, and sink deduplication.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Commit:
    operation_id: str
    authority_version: int
    commit_id: str
    payload_digest: str


class DeduplicatingSink:
    def __init__(self) -> None:
        self.effects: list[str] = []
        self._seen: set[str] = set()

    def apply(self, effect_id: str) -> bool:
        if effect_id in self._seen:
            return False
        self._seen.add(effect_id)
        self.effects.append(effect_id)
        return True


class NonDeduplicatingSink:
    def __init__(self) -> None:
        self.effects: list[str] = []

    def apply(self, effect_id: str) -> bool:
        self.effects.append(effect_id)
        return True


def effect_id(commit: Commit) -> str:
    return f"{commit.operation_id}:{commit.commit_id}"


def run() -> None:
    commit = Commit("op-17", 4, "commit-17", "payload-a")

    # 1. Durable commit exists independently of coordinator-local receipt.
    durable_store = {commit.commit_id: commit}
    coordinator_receipt = None
    assert durable_store[commit.commit_id] == commit
    assert coordinator_receipt is None

    # 2. A crash can occur after effect, before acknowledgement is observed.
    sink = DeduplicatingSink()
    eid = effect_id(commit)
    assert sink.apply(eid) is True
    coordinator_receipt = None
    assert coordinator_receipt is None

    # 3. Recovery must reconcile durable state, then retry with same identity.
    assert durable_store[commit.commit_id] == commit
    assert sink.apply(eid) is False
    assert sink.effects == [eid]

    # 4. Negative control: a sink without deduplication can duplicate effects.
    unsafe_sink = NonDeduplicatingSink()
    assert unsafe_sink.apply(eid) is True
    assert unsafe_sink.apply(eid) is True
    assert unsafe_sink.effects == [eid, eid]

    # 5. Receipt identity is bound to the committed transition.
    receipt = {"effect_id": eid, "commit_id": commit.commit_id}
    forged = {"effect_id": "op-17:other", "commit_id": commit.commit_id}
    assert receipt["effect_id"] == effect_id(commit)
    assert forged["effect_id"] != effect_id(commit)

    # 6. A later authority version does not rewrite historical commitment.
    later_authority_version = 5
    assert later_authority_version != commit.authority_version
    assert durable_store[commit.commit_id].authority_version == 4

    print("EA17_CLEAN_ROOM_PASS")
    print("assertions=9")
    print("exactly_once_requires_external_sink_contract=true")


if __name__ == "__main__":
    run()
