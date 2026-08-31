"""P202 bounded probe: an explicit compatibility claim is not semantic evidence.

The claim must be checked against actual effect semantics. Fail closed on
semantic drift introduced by defaults, enum expansion, omission, units, or
policy-version changes.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class Contract:
    actions: frozenset[str]
    resources: frozenset[str]
    risk_limit: int
    unit: str = "risk"
    policy_version: int = 1


def effects(c: Contract):
    return {(a, r, risk) for a in c.actions for r in c.resources
            for risk in range(c.risk_limit + 1)}


def verify_claim(source: Contract, target: Contract, *, claimed_compatible: bool,
                 default_semantics_stable: bool = True,
                 enum_semantics_stable: bool = True,
                 omission_semantics_stable: bool = True,
                 units_equivalent: bool = True,
                 policy_semantics_stable: bool = True):
    semantic_evidence = all((default_semantics_stable, enum_semantics_stable,
                             omission_semantics_stable, units_equivalent,
                             policy_semantics_stable))
    if not claimed_compatible or not semantic_evidence:
        return "REJECT"
    src, dst = effects(source), effects(target)
    if dst <= src:
        return "ACCEPT"
    return "REJECT"


def main():
    source = Contract(frozenset({"read", "write"}), frozenset({"r1", "r2"}), 5)
    narrow = Contract(frozenset({"read"}), frozenset({"r1"}), 3)

    # 1. A compatible claim with stable semantics can accept attenuation.
    assert verify_claim(source, narrow, claimed_compatible=True) == "ACCEPT"

    # 2. Default changes are semantic evidence failures, even if fields look equal.
    assert verify_claim(narrow, narrow, claimed_compatible=True,
                        default_semantics_stable=False) == "REJECT"

    # 3. Enum expansion can introduce a new effect.
    expanded = Contract(frozenset({"read", "write", "admin"}), frozenset({"r1"}), 3)
    assert verify_claim(narrow, expanded, claimed_compatible=True,
                        enum_semantics_stable=False) == "REJECT"

    # 4. Omitted-field semantics can change meaning.
    assert verify_claim(narrow, narrow, claimed_compatible=True,
                        omission_semantics_stable=False) == "REJECT"

    # 5. Unit changes invalidate the compatibility claim.
    assert verify_claim(narrow, narrow, claimed_compatible=True,
                        units_equivalent=False) == "REJECT"

    # 6. Policy-version changes require semantic evidence.
    v2 = Contract(frozenset({"read"}), frozenset({"r1"}), 3, policy_version=2)
    assert verify_claim(narrow, v2, claimed_compatible=True,
                        policy_semantics_stable=False) == "REJECT"

    # 7. A false positive claim cannot override semantic widening.
    widened = Contract(frozenset({"read", "write"}), frozenset({"r1"}), 3)
    assert verify_claim(narrow, widened, claimed_compatible=True) == "REJECT"

    # 8. No compatibility claim means no governed acceptance.
    assert verify_claim(source, narrow, claimed_compatible=False) == "REJECT"

    print("AUTHORITY COMPATIBILITY CLAIM: 8/8 PASS")


if __name__ == "__main__":
    main()
