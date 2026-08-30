"""Clean-room test: reduce specialized execution observations to generic relations.

This does not assert that the generic relations are Genesis primitives. It asks
whether several execution-specific dimensions can be represented compositionally
without preserving them as dedicated fields.
"""
from dataclasses import dataclass
from itertools import combinations

@dataclass(frozen=True)
class Case:
    label: str
    accepted: bool
    effect_count: int
    evidence_count: int
    revoked: bool
    request_id: str
    version: str
    evidence_binding: str
    authority_epoch: int
    causal_order: str


def generic_relations(c):
    return (
        ("identity", "request", c.request_id),
        ("identity", "evidence", "e1" if c.evidence_count else "none"),
        ("provenance", "evidence_for", c.request_id if c.evidence_binding == "bound" else "other" if c.evidence_binding == "foreign" else "none"),
        ("authority", "epoch", c.authority_epoch),
        ("authority", "accepted", c.accepted),
        ("state", "version", c.version),
        ("state", "revoked", c.revoked),
        ("effect", "count", c.effect_count),
        ("transition", "causal_order", c.causal_order),
        ("evidence", "count", c.evidence_count),
    )


CASES = (
    Case("REVOKED_BEFORE_ACCEPT", False, 0, 0, True, "r1", "v1", "none", 1, "revoke-before-accept"),
    Case("ACCEPTED_THEN_REVOKED", True, 0, 0, True, "r1", "v1", "none", 1, "accept-before-revoke"),
    Case("ONE_EFFECT_UNKNOWN", True, 1, 0, False, "r1", "v1", "bound", 1, "effect-before-ack"),
    Case("DUPLICATE_EFFECT", True, 2, 0, False, "r1", "v1", "bound", 1, "duplicate"),
    Case("VERIFIED", True, 1, 1, False, "r1", "v1", "bound", 1, "verified"),
    Case("PENDING", True, 0, 0, False, "r1", "v1", "none", 1, "pending"),
    Case("FOREIGN_EVIDENCE", True, 1, 1, False, "r1", "v1", "foreign", 1, "verified"),
    Case("STALE_AUTHORITY_EPOCH", True, 1, 1, False, "r1", "v1", "bound", 2, "verified"),
    Case("CAUSALLY_INVALID", True, 1, 1, False, "r1", "v1", "bound", 1, "effect-before-admission"),
)


def projection(c, relation_kinds):
    return tuple(fact for fact in generic_relations(c) if fact[0] in relation_kinds)


def preserves(relation_kinds):
    seen = {}
    for case in CASES:
        key = projection(case, relation_kinds)
        if key in seen and seen[key] != case.label:
            return False
        seen[key] = case.label
    return True


def main():
    all_kinds = ("identity", "provenance", "authority", "state", "effect", "transition", "evidence")
    assert preserves(all_kinds)
    minimal = []
    for size in range(1, len(all_kinds) + 1):
        minimal = [s for s in combinations(all_kinds, size) if preserves(s)]
        if minimal:
            break
    assert minimal
    for kind in minimal[0]:
        reduced = tuple(k for k in all_kinds if k != kind)
        assert not preserves(reduced)
    print("general relational reduction: PASS")
    print(f"minimal_relation_kind_count={len(minimal[0])}")
    print("minimal_relation_kinds=" + "+".join(minimal[0]))
    print("interpretation=execution-specific dimensions are representable by generic relations in this bounded corpus")


if __name__ == "__main__":
    main()
