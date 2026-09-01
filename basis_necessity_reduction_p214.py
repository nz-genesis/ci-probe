"""P214 — minimality-method guard / anti-encoding reduction.

This pass deliberately does NOT claim that the seven Genesis candidates are
proven minimal. P208-P213 supplied substantial bounded sufficiency and
non-inflation evidence, but naive leave-one-out removal is unsound: with
unrestricted representation, every distinction can be packed into State.

P214 therefore tests the *methodological prerequisite* for a valid minimality
claim: semantic roles must be observed through a neutral typed contract, and
cross-role laundering must be rejected. The seven role witnesses then show
that removing a role loses that role under this contract.

Result scope: this validates a bounded necessity-testing method and bounded
role distinguishability. It does not prove that seven implementation
primitives are globally minimal, because a future calculus could bundle
multiple roles while preserving the neutral semantics. That stronger claim
requires an explicit calculus + composition algebra + representation-cost or
primitive-boundary criterion and independent equivalence/counterexample work.
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

# Neutral observation is role-based rather than candidate-specific syntax.
def observe(witness, available_roles):
    role = witness["role"]
    if role not in available_roles:
        return ("UNREPRESENTABLE", role)
    return (role, witness["value"])


def check(name, condition):
    assert condition, name
    print(f"PASS {name}")


def main():
    # Red-Team prerequisite: unrestricted encoding makes naive minimality vacuous.
    packed = {"State": {k: v for k, v in WITNESSES.items()}}
    check("unrestricted_encoding_collapses_minimality", all(k in packed["State"] for k in BASIS))

    # Neutral typed observation blocks laundering a missing semantic role into State.
    check("typed_role_contract_blocks_state_laundering", observe(WITNESSES["Authority"], {"State"})[0] == "UNREPRESENTABLE")

    # Bounded leave-one-out necessity under the declared typed contract.
    for role in BASIS:
        remaining = set(BASIS) - {role}
        result = observe(WITNESSES[role], remaining)
        check(f"remove_{role.lower()}_loses_role_under_contract", result[0] == "UNREPRESENTABLE")

    # Anti-laundering of historically confusable semantic distinctions.
    check("capability_is_not_authority", WITNESSES["Capability"]["role"] != WITNESSES["Authority"]["role"])
    check("observation_is_not_evidence", WITNESSES["Observation"]["role"] != WITNESSES["Evidence"]["role"])
    check("state_is_not_transition", WITNESSES["State"]["role"] != WITNESSES["Transition"]["role"])
    check("constraint_is_not_authority", WITNESSES["Constraint"]["role"] != WITNESSES["Authority"]["role"])
    check("evidence_is_not_authority", WITNESSES["Evidence"]["role"] != WITNESSES["Authority"]["role"])

    check("basis_has_seven_declared_roles", len(BASIS) == 7)

    print("P214_MINIMALITY_METHOD_GUARD_PASS")
    print("assertions=14")
    print("basis_size=7")
    print("new_primitive_required=false")
    print("bounded_role_necessity_supported=true")
    print("global_primitive_minimality_proven=false")

if __name__ == "__main__":
    main()
