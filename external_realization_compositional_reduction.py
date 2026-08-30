"""Clean-room compositional observation reduction experiment.

Generic only. Semantic labels are declared by the witness matrix; the
experiment searches observation-field subsets that preserve all declared
distinctions. It does not infer Genesis ontology or canonical architecture.
"""
from dataclasses import dataclass
from itertools import combinations

@dataclass(frozen=True)
class Witness:
    accepted: bool
    effect_count: int
    acknowledgement: bool
    evidence_count: int
    revoked: bool
    request_id: str
    version: str
    label: str

FIELDS = (
    "accepted", "effect_count", "acknowledgement", "evidence_count",
    "revoked", "request_id", "version",
)

WITNESSES = (
    Witness(False, 0, False, 0, True,  "r1", "v1", "REVOKED_BEFORE_ACCEPT"),
    Witness(True,  0, False, 0, True,  "r1", "v1", "ACCEPTED_THEN_REVOKED"),
    Witness(True,  1, True,  0, False, "r1", "v1", "ONE_EFFECT_UNKNOWN"),
    Witness(True,  2, True,  0, False, "r1", "v1", "DUPLICATE_EFFECT"),
    Witness(True,  1, True,  1, False, "r1", "v1", "VERIFIED"),
    Witness(True,  0, True,  0, False, "r1", "v1", "PENDING"),
    Witness(True,  1, True,  1, False, "r2", "v1", "BOUND_TO_OTHER_REQUEST"),
    Witness(True,  1, True,  0, False, "r1", "v0", "STALE_VERSION"),
)


def projection(w: Witness, fields: tuple[str, ...]):
    return tuple(getattr(w, f) for f in fields)


def preserves_all_distinctions(fields: tuple[str, ...]) -> bool:
    seen = {}
    for w in WITNESSES:
        key = projection(w, fields)
        if key in seen and seen[key] != w.label:
            return False
        seen[key] = w.label
    return True


def minimal_subsets():
    valid = []
    for size in range(len(FIELDS) + 1):
        for fields in combinations(FIELDS, size):
            if preserves_all_distinctions(fields):
                valid.append(fields)
        if valid:
            return valid
    return []


def removal_matrix():
    full = tuple(FIELDS)
    result = {}
    for field in FIELDS:
        reduced = tuple(f for f in full if f != field)
        result[field] = preserves_all_distinctions(reduced)
    return result


def main() -> None:
    mins = minimal_subsets()
    assert mins, "witness matrix must have a distinguishing subset"
    matrix = removal_matrix()
    assert matrix["acknowledgement"] is True
    assert all(matrix[f] is False for f in FIELDS if f != "acknowledgement")
    assert all("acknowledgement" not in subset for subset in mins)
    print("compositional reduction: PASS")
    print(f"minimal_subset_size={len(mins[0])}")
    print("minimal_subsets=" + ";".join("+".join(s) for s in mins))
    print("single_field_removal_preserves=" + ",".join(f for f, ok in matrix.items() if ok))


if __name__ == "__main__":
    main()
