"""Regression suite for circular/common-root attestation."""
from circular_common_root_attestation import Attestation, State, classify, naive_source_majority


def test_common_root_does_not_create_majority_truth() -> None:
    observations = (
        Attestation("a", State.COMPLETE, "root-x"),
        Attestation("b", State.COMPLETE, "root-x"),
        Attestation("c", State.PARTIAL, "root-x"),
    )
    assert naive_source_majority(observations) is State.COMPLETE
    assert classify(observations) is State.UNKNOWN


def test_independent_roots_can_remain_conflicting() -> None:
    observations = (
        Attestation("a", State.COMPLETE, "root-a"),
        Attestation("b", State.PARTIAL, "root-b"),
    )
    assert classify(observations) is State.CONFLICTING


def test_mutual_attestation_without_anchor_is_unknown() -> None:
    observations = (
        Attestation("a", State.COMPLETE, "root-a", True, ("b",)),
        Attestation("b", State.COMPLETE, "root-b", True, ("a",)),
    )
    assert classify(observations) is State.UNKNOWN


def test_three_cycle_without_anchor_is_unknown() -> None:
    observations = (
        Attestation("a", State.COMPLETE, "root-a", True, ("b",)),
        Attestation("b", State.COMPLETE, "root-b", True, ("c",)),
        Attestation("c", State.COMPLETE, "root-c", True, ("a",)),
    )
    assert classify(observations) is State.UNKNOWN


def test_hidden_transitive_common_root_is_unknown() -> None:
    observations = (
        Attestation("a", State.COMPLETE, "root-a", True, ("shared",)),
        Attestation("b", State.COMPLETE, "root-b", True, ("shared",)),
        Attestation("c", State.PARTIAL, "root-c", True),
        Attestation("shared", State.COMPLETE, "root-shared", True),
    )
    assert classify(observations) is State.UNKNOWN


def test_one_consistent_root_is_internal_consistency_only() -> None:
    observations = (
        Attestation("a", State.COMPLETE, "root-a"),
        Attestation("b", State.COMPLETE, "root-a"),
    )
    assert classify(observations) is State.COMPLETE


def test_empty_is_unknown() -> None:
    assert classify(()) is State.UNKNOWN


if __name__ == "__main__":
    tests = (
        test_common_root_does_not_create_majority_truth,
        test_independent_roots_can_remain_conflicting,
        test_mutual_attestation_without_anchor_is_unknown,
        test_three_cycle_without_anchor_is_unknown,
        test_hidden_transitive_common_root_is_unknown,
        test_one_consistent_root_is_internal_consistency_only,
        test_empty_is_unknown,
    )
    for test in tests:
        test()
    print("CIRCULAR COMMON-ROOT ATTESTATION REGRESSION 7/7 PASS")
