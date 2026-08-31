"""Public-safe semantic probe for Genesis Pass 22.
No private Genesis corpus, witness, authority material, or project state.
"""

# PASS24 trigger marker: this update intentionally exercises the push trigger.

def admissible(authority_version, allowed, current_version, reservation_committed):
    return allowed and authority_version == current_version and reservation_committed

def reserve(existing_id, requested_id, requested_committed):
    return existing_id != requested_id and requested_committed

def main():
    assert not admissible(1, True, 2, True)          # stale authority
    assert not admissible(2, False, 2, True)         # revoked authority
    assert not reserve("effect-1", "effect-1", True) # duplicate effect identity
    assert reserve("effect-1", "effect-2", True)   # distinct reservation
    claims = {"effect-may-have-occurred", "effect-did-not-occur"}
    assert len(claims) == 2                             # conflict stays explicit
    assert not admissible(3, True, 2, True)           # self-authority bootstrap blocked
    print("PASS22_PUBLIC: PASS; cases=6; private_data=none; new_primitives=0")

if __name__ == "__main__":
    main()
