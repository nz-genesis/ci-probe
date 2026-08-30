"""Clean-room stress test for stability of a reduced observation basis.

The experiment deliberately adds independent adversarial witness distinctions
and checks whether the previously reduced basis remains sufficient. A failure
is evidence of corpus incompleteness, not a reason to invent a new primitive.
"""
from dataclasses import dataclass
from itertools import combinations

BASE_FIELDS = (
    "accepted", "effect_count", "evidence_count", "revoked", "request_id", "version"
)
EXTENDED_FIELDS = BASE_FIELDS + (
    "evidence_binding", "authority_epoch", "causal_order"
)


@dataclass(frozen=True)
class Witness:
    accepted: bool
    effect_count: int
    evidence_count: int
    revoked: bool
    request_id: str
    version: str
    evidence_binding: str
    authority_epoch: int
    causal_order: str
    label: str


WITNESSES = (
    Witness(False, 0, 0, True,  "r1", "v1", "none", 1, "revoke-before-accept", "REVOKED_BEFORE_ACCEPT"),
    Witness(True,  0, 0, True,  "r1", "v1", "none", 1, "accept-before-revoke", "ACCEPTED_THEN_REVOKED"),
    Witness(True,  1, 0, False, "r1", "v1", "bound", 1, "effect-before-ack", "ONE_EFFECT_UNKNOWN"),
    Witness(True,  2, 0, False, "r1", "v1", "bound", 1, "duplicate", "DUPLICATE_EFFECT"),
    Witness(True,  1, 1, False, "r1", "v1", "bound", 1, "verified", "VERIFIED"),
    Witness(True,  0, 0, False, "r1", "v1", "none", 1, "pending", "PENDING"),
    Witness(True,  1, 1, False, "r1", "v1", "foreign", 1, "verified", "FOREIGN_EVIDENCE"),
    Witness(True,  1, 1, False, "r1", "v1", "bound", 2, "verified", "STALE_AUTHORITY_EPOCH"),
    Witness(True,  1, 1, False, "r1", "v1", "bound", 1, "effect-before-admission", "CAUSALLY_INVALID"),
)


def projection(w, fields):
    return tuple(getattr(w, field) for field in fields)


def preserves(fields):
    seen = {}
    for witness in WITNESSES:
        key = projection(witness, fields)
        prior = seen.get(key)
        if prior is not None and prior != witness.label:
            return False
        seen[key] = witness.label
    return True


def minimal(fields):
    for size in range(len(fields) + 1):
        valid = [subset for subset in combinations(fields, size) if preserves(subset)]
        if valid:
            return valid
    return []


def main():
    assert preserves(BASE_FIELDS) is False
    mins = minimal(EXTENDED_FIELDS)
    assert mins
    assert all("acknowledgement" not in subset for subset in mins)
    required = {"evidence_binding", "authority_epoch", "causal_order"}
    assert required.issubset(set(mins[0]))
    print("stable basis stress: PASS")
    print(f"old_basis_preserved={preserves(BASE_FIELDS)}")
    print(f"extended_minimal_subset_size={len(mins[0])}")
    print("extended_minimal_subset=" + "+".join(mins[0]))
    print("new_distinction_fields=evidence_binding,authority_epoch,causal_order")


if __name__ == "__main__":
    main()
