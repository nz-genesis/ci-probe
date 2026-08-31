"""P200 bounded probe: multi-hop delegation must compose monotonically.

The probe compares semantic effects, not merely the syntax of each authority
record. A descendant may only retain effects that are already permitted by
its complete ancestor chain. Sibling authorities are never unioned.
"""

from dataclasses import dataclass


ALIASES = {"remove": "delete", "read_only": "read"}


@dataclass(frozen=True)
class Authority:
    actions: frozenset[str]
    resources: frozenset[str]
    risk_limit: int


def canonical_action(action: str) -> str:
    return ALIASES.get(action, action)


def effects(authority: Authority) -> set[tuple[str, str, int]]:
    return {
        (canonical_action(action), resource, risk)
        for action in authority.actions
        for resource in authority.resources
        for risk in range(authority.risk_limit + 1)
    }


def compose(parent_effects: set[tuple[str, str, int]], child: Authority):
    child_effects = effects(child)
    if not child_effects.issubset(parent_effects):
        return None
    return child_effects


def chain_compose(chain: list[Authority]):
    if not chain:
        return set()
    current = effects(chain[0])
    for child in chain[1:]:
        current = compose(current, child)
        if current is None:
            return None
    return current


def main():
    root = Authority(frozenset({"read", "write"}), frozenset({"r1", "r2"}), 5)
    mid = Authority(frozenset({"read", "write"}), frozenset({"r1"}), 3)
    leaf = Authority(frozenset({"read"}), frozenset({"r1"}), 2)

    # 1. Valid multi-hop attenuation composes.
    assert chain_compose([root, mid, leaf]) == effects(leaf)

    # 2. Effective leaf authority remains bounded by the root.
    assert chain_compose([root, mid, leaf]).issubset(effects(root))

    # 3. Action escalation at the second hop is rejected.
    action_escalation = Authority(frozenset({"read", "delete"}), frozenset({"r1"}), 2)
    assert chain_compose([root, mid, action_escalation]) is None

    # 4. Resource escalation at the second hop is rejected.
    resource_escalation = Authority(frozenset({"read"}), frozenset({"r1", "r2"}), 2)
    assert chain_compose([root, mid, resource_escalation]) is None

    # 5. Risk escalation hidden at the leaf is rejected.
    risk_escalation = Authority(frozenset({"read"}), frozenset({"r1"}), 4)
    assert chain_compose([root, mid, risk_escalation]) is None

    # 6. A semantic alias cannot launder an action escalation.
    alias_escalation = Authority(frozenset({"remove"}), frozenset({"r1"}), 2)
    assert chain_compose([root, mid, alias_escalation]) is None

    # 7. Nearest-parent laundering is rejected: B is already wider than A.
    widened_mid = Authority(frozenset({"read", "write"}), frozenset({"r1", "r2"}), 6)
    narrower_leaf = Authority(frozenset({"read"}), frozenset({"r1"}), 1)
    assert chain_compose([root, widened_mid, narrower_leaf]) is None

    # 8. Sibling authorities are not unioned into a new authority.
    sibling_a = Authority(frozenset({"read"}), frozenset({"r1"}), 2)
    sibling_b = Authority(frozenset({"write"}), frozenset({"r2"}), 2)
    union_like = Authority(frozenset({"read", "write"}), frozenset({"r1", "r2"}), 2)
    assert chain_compose([root, sibling_a]) == effects(sibling_a)
    assert chain_compose([root, sibling_b]) == effects(sibling_b)
    assert chain_compose([root, sibling_a, union_like]) is None

    # 9. Full semantic intersection can only shrink across hops.
    c1 = Authority(frozenset({"read", "write"}), frozenset({"r1"}), 4)
    c2 = Authority(frozenset({"read"}), frozenset({"r1"}), 1)
    e_root = effects(root)
    e_c1 = chain_compose([root, c1])
    e_c2 = chain_compose([root, c1, c2])
    assert e_c2.issubset(e_c1) and e_c1.issubset(e_root)

    # 10. Empty semantic scope is safe and never creates new authority.
    empty = Authority(frozenset(), frozenset({"r1"}), 0)
    assert chain_compose([root, empty]) == set()

    print("SEMANTIC EFFECTIVE AUTHORITY COMPOSITION: 10/10 PASS")


if __name__ == "__main__":
    main()
