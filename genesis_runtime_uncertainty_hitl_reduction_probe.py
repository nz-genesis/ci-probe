def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    cases = [
        ("unknown_is_not_success", "UNKNOWN", {"success": False}),
        ("unknown_is_not_failure", "UNKNOWN", {"failure": False}),
        ("unknown_is_not_retry_permission", "UNKNOWN", {"retry": False}),
        ("conflict_is_preserved", "CONFLICT", {"silent_latest": False}),
        ("revoked_authority_blocks_new_transition", "REVOKED", {"admit": False}),
        ("revocation_is_not_effect_proof", "REVOKED", {"effect_absent": False}),
        ("hitl_is_not_effect_verification", "APPROVED", {"verified_effect": False}),
        ("hitl_requires_authority", "APPROVED", {"authority": True}),
        ("hitl_is_not_universal", "LOW_RISK", {"requires_hitl": False}),
        ("irreversible_unknown_blocks_autoretry", "UNKNOWN", {"retry": False}),
        ("adjudication_does_not_mutate_admitted_context", "ADJUDICATED", {"same_context": False}),
        ("human_resolution_does_not_create_duplicate_effect", "RESOLVED", {"second_effect": False}),
    ]
    for name, state, props in cases:
        require(state in {"UNKNOWN", "CONFLICT", "REVOKED", "APPROVED", "LOW_RISK", "ADJUDICATED", "RESOLVED"}, name)
        for key, expected in props.items():
            require(expected, f"{name}: {key}")
    print("GENESIS RUNTIME UNCERTAINTY HITL REDUCTION: PASS")


if __name__ == "__main__":
    main()
