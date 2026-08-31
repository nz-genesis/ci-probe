"""P198 bounded probe: publication authority must be fresh at publication time."""


def can_publish(state, now):
    authority = state["authority"]
    contract = state["contract"]
    if not authority["granted"]:
        return False, "UNAUTHORIZED"
    if now > authority["expires_at"]:
        return False, "AUTHORITY_EXPIRED"
    if authority["contract_version"] != contract["version"]:
        return False, "CONTRACT_DRIFT"
    return True, "PUBLISH"


def main():
    base = {
        "authority": {"granted": True, "expires_at": 10, "contract_version": 1},
        "contract": {"version": 1},
    }

    # Fresh authority at derivation and publication permits publication.
    ok, reason = can_publish(base, 5)
    assert ok and reason == "PUBLISH"

    # Expiry between derivation and publication blocks publication.
    ok, reason = can_publish(base, 11)
    assert not ok and reason == "AUTHORITY_EXPIRED"

    # Exact expiry boundary remains valid under the explicit <= rule.
    ok, reason = can_publish(base, 10)
    assert ok and reason == "PUBLISH"

    # Revocation after derivation must be observed at publication.
    revoked = {**base, "authority": {**base["authority"], "granted": False}}
    ok, reason = can_publish(revoked, 5)
    assert not ok and reason == "UNAUTHORIZED"

    # Contract drift invalidates an otherwise unexpired admission.
    drifted = {**base, "contract": {"version": 2}}
    ok, reason = can_publish(drifted, 5)
    assert not ok and reason == "CONTRACT_DRIFT"

    # A refreshed authority bound to the new contract can publish.
    refreshed = {**drifted, "authority": {"granted": True, "expires_at": 20, "contract_version": 2}}
    ok, reason = can_publish(refreshed, 15)
    assert ok and reason == "PUBLISH"

    # A stale authority cannot be revived by a fresh contract alone.
    stale = {**drifted, "authority": {"granted": True, "expires_at": 10, "contract_version": 1}}
    ok, reason = can_publish(stale, 5)
    assert not ok and reason == "CONTRACT_DRIFT"

    # Publication must not rely on an admission decision cached at derivation time.
    derived_decision = True
    late_revocation = {**base, "authority": {**base["authority"], "granted": False}}
    ok, reason = can_publish(late_revocation, 5)
    assert derived_decision is True and not ok and reason == "UNAUTHORIZED"

    print("TEMPORAL PUBLICATION AUTHORITY: 8/8 PASS")


if __name__ == "__main__":
    main()
