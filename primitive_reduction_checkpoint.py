"""Clean-room primitive-reduction checkpoint.

The experiment uses seven anonymous semantic dimensions (d0..d6). The names
are deliberately opaque so this public artifact does not expose private
architecture or ontology hypotheses.

Question: within a bounded accumulated witness corpus, can any dimension be
functionally reconstructed from the other six? If not, removing that dimension
creates a collision in the witness corpus. This is bounded evidence only; it
is not a claim of universal ontology or primitive status.
"""

from __future__ import annotations

from itertools import combinations

ROWS = [
    ("a", 0, 0, 0, 0, 0, 0, 0),
    ("b", 1, 0, 0, 0, 0, 0, 0),
    ("c", 0, 1, 0, 0, 0, 0, 0),
    ("d", 0, 0, 1, 0, 0, 0, 0),
    ("e", 0, 0, 0, 1, 0, 0, 0),
    ("f", 0, 0, 0, 0, 1, 0, 0),
    ("g", 0, 0, 0, 0, 0, 1, 0),
    ("h", 0, 0, 0, 0, 0, 0, 1),
    ("i", 1, 1, 0, 0, 0, 0, 0),
    ("j", 0, 1, 1, 0, 0, 0, 0),
    ("k", 0, 0, 1, 1, 0, 0, 0),
    ("l", 0, 0, 0, 1, 1, 0, 0),
    ("m", 0, 0, 0, 0, 1, 1, 0),
    ("n", 0, 0, 0, 0, 0, 1, 1),
    ("o", 1, 0, 0, 0, 0, 0, 1),
    ("p", 1, 0, 1, 0, 1, 0, 0),
    ("q", 0, 1, 0, 1, 0, 1, 0),
    ("r", 0, 0, 1, 0, 0, 1, 1),
    ("s", 1, 1, 1, 1, 0, 0, 0),
    ("t", 0, 1, 1, 1, 1, 0, 0),
    ("u", 0, 0, 1, 1, 1, 1, 0),
    ("v", 0, 0, 0, 1, 1, 1, 1),
    ("w", 1, 1, 0, 0, 1, 1, 1),
    ("x", 1, 0, 1, 1, 0, 1, 1),
]

DIMENSIONS = range(1, 8)


def projection(row: tuple[str, int, int, int, int, int, int, int], removed: int) -> tuple[int, ...]:
    return tuple(row[i] for i in DIMENSIONS if i != removed)


def has_collision(removed: int) -> bool:
    seen: dict[tuple[int, ...], str] = {}
    for row in ROWS:
        key = projection(row, removed)
        previous = seen.get(key)
        if previous is not None and previous != row[0]:
            return True
        seen[key] = row[0]
    return False


def is_functionally_reconstructible(target: int) -> bool:
    groups: dict[tuple[int, ...], set[int]] = {}
    for row in ROWS:
        key = projection(row, target)
        groups.setdefault(key, set()).add(row[target])
    return all(len(values) <= 1 for values in groups.values())


def minimal_unique_subsets() -> list[tuple[int, ...]]:
    solutions: list[tuple[int, ...]] = []
    for size in range(1, len(tuple(DIMENSIONS)) + 1):
        for subset in combinations(tuple(DIMENSIONS), size):
            projections = {tuple(row[i] for i in subset) for row in ROWS}
            if len(projections) == len(ROWS):
                solutions.append(subset)
        if solutions:
            break
    return solutions


def main() -> None:
    assert len(ROWS) == 24
    assert len({row[0] for row in ROWS}) == len(ROWS)

    results = []
    for dimension in DIMENSIONS:
        collision = has_collision(dimension)
        reconstructible = is_functionally_reconstructible(dimension)
        assert collision, (dimension, "expected removal collision")
        assert not reconstructible, (dimension, "unexpected functional dependency")
        results.append((dimension, collision, reconstructible))

    minimal = minimal_unique_subsets()
    assert minimal == [(1, 2, 3, 4, 5, 6, 7)], minimal

    print("PASS: 24-row bounded witness corpus")
    print("PASS: each of 7 dimensions has an independent removal collision")
    print("PASS: no dimension is functionally reconstructible from the other six")
    print("PASS: unique identification of the current corpus requires all 7 dimensions")
    print("PASS: result is bounded to this corpus; no universal primitive claim")


if __name__ == "__main__":
    main()
