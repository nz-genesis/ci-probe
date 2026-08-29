"""Regression suite for adversarial provenance claims."""
from adversarial_provenance_claims import Observation, State, classify, naive_declared_majority


def test_false_independence_does_not_create_majority_truth() -> None:
    observations = (
        Observation(State.COMPLETE, "claimed-a", False),
        Observation(State.COMPLETE, "claimed-b", False),
        Observation(State.PARTIAL, "verified-c", True),
    )
    assert naive_declared_majority(observations) is State.COMPLETE
    assert classify(observations) is State.UNKNOWN


def test_verified_disagreement_is_conflict() -> None:
    observations = (
        Observation(State.COMPLETE, "verified-a", True),
        Observation(State.PARTIAL, "verified-b", True),
    )
    assert classify(observations) is State.CONFLICTING


def test_unverifiable_contradiction_stays_unknown() -> None:
    observations = (
        Observation(State.COMPLETE, "verified-a", True),
        Observation(State.PARTIAL, "claimed-b", False),
    )
    assert classify(observations) is State.UNKNOWN


def test_verified_single_group_is_only_internal_consistency() -> None:
    observations = (
        Observation(State.COMPLETE, "verified-a", True),
        Observation(State.COMPLETE, "verified-a", True),
    )
    assert classify(observations) is State.COMPLETE


def test_empty_is_unknown() -> None:
    assert classify(()) is State.UNKNOWN


if __name__ == "__main__":
    tests = (
        test_false_independence_does_not_create_majority_truth,
        test_verified_disagreement_is_conflict,
        test_unverifiable_contradiction_stays_unknown,
        test_verified_single_group_is_only_internal_consistency,
        test_empty_is_unknown,
    )
    for test in tests:
        test()
    print("ADVERSARIAL PROVENANCE CLAIMS REGRESSION 5/5 PASS")
