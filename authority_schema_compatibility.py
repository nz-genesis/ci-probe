"""P201 bounded probe: authority schema conversion must preserve semantic safety.

A conversion may be equivalent, attenuating, widening, or incomparable. Unknown
or incomparable semantics are never treated as equivalent for governed action.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Authority:
    actions: frozenset[str]
    resources: frozenset[str]
    risk_limit: int


def effects(a: Authority) -> set[tuple[str, str, int]]:
    return {(action, resource, risk)
            for action in a.actions
            for resource in a.resources
            for risk in range(a.risk_limit + 1)}


def classify(source: Authority, target: Authority, *, schema_compatible: bool):
    if not schema_compatible:
        return "INCOMPARABLE"
    src, dst = effects(source), effects(target)
    if dst == src:
        return "EQUIVALENT"
    if dst < src:
        return "ATTENUATED"
    if src < dst:
        return "WIDENED"
    return "INCOMPARABLE"


def governed_conversion(source, target, *, schema_compatible):
    relation = classify(source, target, schema_compatible=schema_compatible)
    if relation in {"EQUIVALENT", "ATTENUATED"}:
        return "ACCEPT"
    return "REJECT"


def main():
    root = Authority(frozenset({"read", "write"}), frozenset({"r1", "r2"}), 5)

    # 1. Same semantics across compatible schema versions.
    assert classify(root, root, schema_compatible=True) == "EQUIVALENT"
    assert governed_conversion(root, root, schema_compatible=True) == "ACCEPT"

    # 2. Explicit narrowing is safe.
    narrow = Authority(frozenset({"read"}), frozenset({"r1"}), 3)
    assert classify(root, narrow, schema_compatible=True) == "ATTENUATED"
    assert governed_conversion(root, narrow, schema_compatible=True) == "ACCEPT"

    # 3. Action widening is rejected.
    action_widen = Authority(frozenset({"read", "write", "delete"}), frozenset({"r1"}), 3)
    assert classify(narrow, action_widen, schema_compatible=True) == "WIDENED"
    assert governed_conversion(narrow, action_widen, schema_compatible=True) == "REJECT"

    # 4. Resource widening is rejected.
    resource_widen = Authority(frozenset({"read"}), frozenset({"r1", "r2"}), 3)
    assert classify(narrow, resource_widen, schema_compatible=True) == "WIDENED"
    assert governed_conversion(narrow, resource_widen, schema_compatible=True) == "REJECT"

    # 5. Risk widening is rejected.
    risk_widen = Authority(frozenset({"read"}), frozenset({"r1"}), 5)
    assert classify(narrow, risk_widen, schema_compatible=True) == "WIDENED"
    assert governed_conversion(narrow, risk_widen, schema_compatible=True) == "REJECT"

    # 6. Disjoint semantics are not forced into an ordering.
    disjoint = Authority(frozenset({"read"}), frozenset({"r2"}), 3)
    assert classify(narrow, disjoint, schema_compatible=True) == "INCOMPARABLE"
    assert governed_conversion(narrow, disjoint, schema_compatible=True) == "REJECT"

    # 7. Schema incompatibility blocks even byte-for-byte-looking content.
    assert classify(narrow, narrow, schema_compatible=False) == "INCOMPARABLE"
    assert governed_conversion(narrow, narrow, schema_compatible=False) == "REJECT"

    # 8. Unknown/new target semantics cannot be accepted merely because known
    # fields attenuate: an incomparable target must fail closed.
    known = Authority(frozenset({"read"}), frozenset({"r1"}), 2)
    unknown_semantics = Authority(frozenset({"read", "admin"}), frozenset({"r1"}), 2)
    assert classify(known, unknown_semantics, schema_compatible=False) == "INCOMPARABLE"
    assert governed_conversion(known, unknown_semantics, schema_compatible=False) == "REJECT"

    print("AUTHORITY SCHEMA COMPATIBILITY: 8/8 PASS")


if __name__ == "__main__":
    main()
