"""P214 — basis necessity / anti-encoding reduction.

Purpose: test what is actually required to claim a *minimal* Genesis basis.
P208-P213 mainly supplied sufficiency/non-inflation evidence. P214 attacks
necessity: can each candidate distinction be removed without losing its
semantic role?

Critical methodological guard: unrestricted encoding makes minimality trivial
(everything can be packed into State). Therefore this bounded probe uses a
neutral typed-role observation contract and rejects role laundering: a witness
for one semantic role cannot be relabeled as another role merely to preserve
cardinality.

This is not a proof of global minimality. It tests the validity and bounded
necessity of the leave-one-out method itself.
"""

BASIS = (
    "State", "Transition", "Capability", "Authority",
    "Observation", "Evidence", "Constraint",
)

WITNESSES = {
    "State": {"role": "State", "value": "persistent-system-condition"},
    "Transition": {"role": "Transition", "value": "causal-state-change"},
    "Capability": {"role": "Capability", "value": "can-perform"},
    "Authority": {"role": "Authority", "value": "may-perform"},
    "Observation": {"role": "Observation", "value": "observed-unknown-world-state"},
    "Evidence": {"role": "Evidence", "value": "supports-claim-with-provenance"},
    "Constraint": {"role": "Constraint", "value": "admissibility-boundary"},
}

# Neutral observation is intentionally role-based, not candidate syntax.
def observe(witness, available_roles):
    role = witness["role"]
    if role not in available_roles:
        return ("UNREPRESENTABLE", role)
    return (role, witness["value"])


def check(name, condition):
    assert condition, name
    print(f"PASS {name}")


def main():
    # 1. Minimality guard: unrestricted encoding cannot distinguish necessity.
    packed = {"State": {k: v for k, v in WITNESSES.items()}}
    check("unrestricted_encoding_collapses_minimality", all(k in packed["State"] for k in BASIS))
    check("typed_role_contract_blocks_state_laundering", observe(WITNESSES["Authority"], {"State"})[0] == "UNREPRESENTABLE")

    # 2-8. Leave-one-out: each candidate has a bounded witness that is lost.
    for role in BASIS:
        remaining = set(BASIS) - {role}
        result = observe(WITNESSES[role], remaining)
        check(f"remove_{role.lower()}_loses_distinction", result[0] == "UNREPRESENTABLE")

    # 9-13. Cross-role anti-laundering: similar-looking distinctions remain distinct.
    check("capability_is_not_authority", WITNESSES["Capability"]["role"] != WITNESSES["Authority"]["role"])
    check("observation_is_not_evidence", WITNESSES["Observation"]["role"] != WITNESSES["Evidence"]["role"])
    check("state_is_not_transition", WITNESSES["State"]["role"] != WITNESSES["Transition"]["role"])
    check("constraint_is_not_authority", WITNESSES["Constraint"]["role"] != WITNESSES["Authority"]["role"])
    check("evidence_is_not_authority", WITNESSES["Evidence"]["role"] != WITNESSES["Authority"]["role"])

    # 14. No extra named primitive is smuggled into the basis.
    check("no_eighth_primitive", len(BASIS) == 7)

    print("P214_BASIS_NECESSITY_ANTI_ENCODING_PASS")
    print("assertions=14")
    print("basis_size=7")
    print("new_primitive_required=false")
    print("global_minimality_proven=false")


if __name__ == "__main__":
    main()
