"""Regression checks for primitive-removal K."""

from primitive_removal_k import CANDIDATES, FIXTURES, composite_reencoding, projection_collides


def test_each_dimension_is_semantically_distinguishable() -> None:
    for candidate in CANDIDATES:
        left, right = FIXTURES[candidate]
        assert left.as_dict()[candidate] != right.as_dict()[candidate]
        assert projection_collides(candidate)


def test_named_primitive_is_not_required_for_representation() -> None:
    for candidate in CANDIDATES:
        left, right = FIXTURES[candidate]
        assert composite_reencoding(left, candidate) != composite_reencoding(right, candidate)


def test_reencoding_is_uniform() -> None:
    shapes = set()
    for candidate in CANDIDATES:
        left, _ = FIXTURES[candidate]
        encoded = composite_reencoding(left, candidate)
        shapes.add(tuple(key for key, _ in encoded))
    assert len(shapes) == 1


if __name__ == "__main__":
    test_each_dimension_is_semantically_distinguishable()
    test_named_primitive_is_not_required_for_representation()
    test_reencoding_is_uniform()
    print("primitive removal K tests: PASS")
