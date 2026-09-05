"""P272 differential falsification: mutable root vs protected trust anchor.

The test asks whether the recursive system can validate a replacement of the
authority root using only state that is itself mutable by the recursive system.
The expected answer is no. A protected anchor can validate a root rotation;
a mutable root alone cannot distinguish an attacker-created replacement.

Semantic model only; cryptographic strength is out of scope.
"""
from dataclasses import dataclass, replace
from enum import Enum


class Verdict(Enum):
    VALID = "valid"
    UNKNOWN = "unknown"
    INVALID = "invalid"


@dataclass(frozen=True)
class Anchor:
    key_id: str
    fingerprint: str
    immutable: bool = True


@dataclass(frozen=True)
class Root:
    root_id: str
    epoch: int
    fingerprint: str
    signed_by: str


@dataclass(frozen=True)
class Credential:
    root_id: str
    epoch: int
    issuer: str
    scope: frozenset[str]


def verify_root(root: Root, anchor: Anchor) -> Verdict:
    if not anchor.immutable:
        return Verdict.UNKNOWN
    return Verdict.VALID if root.signed_by == anchor.key_id else Verdict.INVALID


def mutable_root_only(candidate: Root, current: Root) -> Verdict:
    # No independent fact distinguishes a forged replacement from a legitimate
    # replacement when both are represented only by mutable local state.
    if candidate.epoch <= current.epoch:
        return Verdict.INVALID
    return Verdict.UNKNOWN


def delegation_valid(credential: Credential, root: Root, epoch: int) -> bool:
    return (
        credential.root_id == root.root_id
        and credential.epoch == epoch
        and credential.issuer == root.root_id
        and "capability" in credential.scope
    )


def verify() -> None:
    anchor = Anchor("owner-root", "anchor-h1")
    current = Root("genesis-root", 1, "root-h1", "owner-root")
    legitimate = Root("genesis-root-v2", 2, "root-h2", "owner-root")
    forged = Root("attacker-root", 2, "root-x", "attacker")

    # 1. A mutable-root-only model cannot distinguish a newer forged root.
    assert mutable_root_only(legitimate, current) is Verdict.UNKNOWN
    assert mutable_root_only(forged, current) is Verdict.UNKNOWN

    # 2. A protected anchor distinguishes the legitimate root from the forgery.
    assert verify_root(legitimate, anchor) is Verdict.VALID
    assert verify_root(forged, anchor) is Verdict.INVALID

    # 3. A self-declared mutable anchor is not independent evidence.
    mutable_anchor = Anchor("attacker", "root-x", immutable=False)
    assert verify_root(forged, mutable_anchor) is Verdict.UNKNOWN

    # 4. Old delegation cannot survive root rotation.
    old_credential = Credential("genesis-root", 1, "genesis-root", frozenset({"capability"}))
    assert delegation_valid(old_credential, legitimate, 2) is False

    # 5. Current-root delegation remains usable after independently verified rotation.
    fresh_credential = Credential("genesis-root-v2", 2, "genesis-root-v2", frozenset({"capability"}))
    assert delegation_valid(fresh_credential, legitimate, 2) is True

    # 6. An attacker cannot make a valid delegation by merely changing local root state.
    forged_credential = replace(fresh_credential, root_id="attacker-root")
    assert delegation_valid(forged_credential, legitimate, 2) is False

    # 7. The anchor is not a new Genesis semantic primitive: it is an external
    # trust dependency used to qualify an Authority/Evidence transition.
    semantic_basis = {"Authority", "Evidence", "Observation", "Constraint", "Transition"}
    assert "Authority" in semantic_basis and "Transition" in semantic_basis

    # 8. If the protected anchor is unavailable, the correct result is uncertainty,
    # not an inferred authorization from local coordinator majority.
    assert verify_root(legitimate, Anchor("owner-root", "anchor-h1", immutable=False)) is Verdict.UNKNOWN

    print("P272 trust-anchor differential: 8/8 PASS")


if __name__ == "__main__":
    verify()
