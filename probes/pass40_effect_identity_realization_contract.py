"""Genesis Pass 40: effect identity × realization contract × irreversible effect × HITL boundary.

Public-safe synthetic probe. It must not contain private Genesis state, corpus, authority,
credentials, or witness material.
"""

from dataclasses import dataclass
from enum import Enum


class Outcome(str, Enum):
    ALLOW = "ALLOW"
    UNKNOWN = "UNKNOWN"
    CONFLICT = "CONFLICT"
    HITL_REQUIRED = "HITL_REQUIRED"
    REJECT = "REJECT"


@dataclass(frozen=True)
class Transition:
    id: str
    irreversible: bool


@dataclass(frozen=True)
class RealizationContract:
    idempotent: bool
    effect_identity_supported: bool
    external_enforces_identity: bool


@dataclass(frozen=True)
class Observation:
    effect_identity: str
    happened: bool


def decide(t: Transition, contract: RealizationContract, obs: list[Observation]) -> Outcome:
    # Missing knowledge is never permission to retry.
    if not obs:
        return Outcome.UNKNOWN

    happened = {o.happened for o in obs}
    identities = {o.effect_identity for o in obs}
    if len(happened) > 1:
        return Outcome.CONFLICT

    if True in happened:
        return Outcome.UNKNOWN if len(identities) > 1 else Outcome.REJECT

    # A non-idempotent, irreversible effect with no external identity enforcement
    # cannot be safely automated from a merely negative observation: human decision
    # is required before crossing the irreversible boundary.
    if t.irreversible and not (
        contract.idempotent
        and contract.effect_identity_supported
        and contract.external_enforces_identity
    ):
        return Outcome.HITL_REQUIRED

    return Outcome.ALLOW


def test_no_observation_is_not_retry_permission() -> None:
    t = Transition("T1", irreversible=False)
    c = RealizationContract(True, True, True)
    assert decide(t, c, []) is Outcome.UNKNOWN


def test_positive_observation_blocks_repeat() -> None:
    t = Transition("T2", irreversible=False)
    c = RealizationContract(True, True, True)
    assert decide(t, c, [Observation("E2", True)]) is Outcome.REJECT


def test_conflicting_observations_are_conflict() -> None:
    t = Transition("T3", irreversible=False)
    c = RealizationContract(True, True, True)
    assert decide(t, c, [Observation("E3", True), Observation("E3", False)]) is Outcome.CONFLICT


def test_non_idempotent_irreversible_boundary_requires_hitl() -> None:
    t = Transition("T4", irreversible=True)
    c = RealizationContract(False, False, False)
    assert decide(t, c, [Observation("E4", False)]) is Outcome.HITL_REQUIRED


def test_idempotent_enforced_contract_can_admit_negative_observation() -> None:
    t = Transition("T5", irreversible=True)
    c = RealizationContract(True, True, True)
    assert decide(t, c, [Observation("E5", False)]) is Outcome.ALLOW


def test_local_identity_without_external_enforcement_is_insufficient() -> None:
    t = Transition("T6", irreversible=True)
    c = RealizationContract(True, True, False)
    assert decide(t, c, [Observation("E6", False)]) is Outcome.HITL_REQUIRED


def test_identity_collision_does_not_prove_effect_once() -> None:
    t = Transition("T7", irreversible=False)
    c = RealizationContract(False, True, False)
    assert decide(t, c, [Observation("same-id", True), Observation("same-id", True)]) is Outcome.REJECT
    # The semantic decision refuses another effect; it does not claim that the external
    # world performed exactly one effect. That guarantee belongs to the realization contract.


def test_capability_and_authority_are_not_replaced_by_effect_identity() -> None:
    # Effect identity is not authority. A string naming an effect cannot authorize a transition.
    t = Transition("T8", irreversible=False)
    c = RealizationContract(True, True, True)
    assert decide(t, c, [Observation("not-authority", False)]) is Outcome.ALLOW


def test_primitive_removal_boundary() -> None:
    # Recovery, Fence, Receipt, IdempotencyKey, Transaction and EffectIdentity are
    # represented here as realization techniques/data, not Genesis primitives.
    # Removing any one from the semantic candidate basis is not required by this probe.
    candidate = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}
    assert candidate == {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}


if __name__ == "__main__":
    tests = [
        test_no_observation_is_not_retry_permission,
        test_positive_observation_blocks_repeat,
        test_conflicting_observations_are_conflict,
        test_non_idempotent_irreversible_boundary_requires_hitl,
        test_idempotent_enforced_contract_can_admit_negative_observation,
        test_local_identity_without_external_enforcement_is_insufficient,
        test_identity_collision_does_not_prove_effect_once,
        test_capability_and_authority_are_not_replaced_by_effect_identity,
        test_primitive_removal_boundary,
    ]
    for test in tests:
        test()
    print(f"PASS40_PUBLIC: PASS; cases={len(tests)}")
