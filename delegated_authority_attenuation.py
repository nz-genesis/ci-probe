"""P199 bounded probe: delegated authority must not exceed its parent."""


def is_attenuated(parent, child):
    if not child["actions"].issubset(parent["actions"]):
        return False, "ACTION_SCOPE_ESCALATION"
    if not child["resources"].issubset(parent["resources"]):
        return False, "RESOURCE_SCOPE_ESCALATION"
    if child["expires_at"] > parent["expires_at"]:
        return False, "EXPIRY_EXTENSION"
    if child["risk_limit"] > parent["risk_limit"]:
        return False, "RISK_SCOPE_ESCALATION"
    return True, "ATTENUATED"


def main():
    parent = {
        "actions": {"read", "write"},
        "resources": {"r1", "r2"},
        "expires_at": 100,
        "risk_limit": 5,
    }

    # Strictly narrower action and resource scope is valid.
    child = {
        "actions": {"read"}, "resources": {"r1"},
        "expires_at": 90, "risk_limit": 3,
    }
    assert is_attenuated(parent, child) == (True, "ATTENUATED")

    # Equal scope remains non-escalating.
    equal = dict(parent)
    equal["actions"] = set(parent["actions"])
    equal["resources"] = set(parent["resources"])
    assert is_attenuated(parent, equal) == (True, "ATTENUATED")

    # Child cannot add an action.
    action_escalation = {**child, "actions": {"read", "delete"}}
    assert is_attenuated(parent, action_escalation) == (False, "ACTION_SCOPE_ESCALATION")

    # Child cannot add a resource.
    resource_escalation = {**child, "resources": {"r1", "r3"}}
    assert is_attenuated(parent, resource_escalation) == (False, "RESOURCE_SCOPE_ESCALATION")

    # Child cannot outlive parent authority.
    expiry_extension = {**child, "expires_at": 101}
    assert is_attenuated(parent, expiry_extension) == (False, "EXPIRY_EXTENSION")

    # Child cannot increase permitted risk.
    risk_extension = {**child, "risk_limit": 6}
    assert is_attenuated(parent, risk_extension) == (False, "RISK_SCOPE_ESCALATION")

    # Narrowing multiple dimensions simultaneously remains valid.
    narrow = {
        "actions": set(), "resources": set(),
        "expires_at": 1, "risk_limit": 0,
    }
    assert is_attenuated(parent, narrow) == (True, "ATTENUATED")

    # A child with a wider scope in only one dimension is still invalid.
    one_dimension = {**child, "resources": {"r1", "r2", "r3"}}
    assert is_attenuated(parent, one_dimension) == (False, "RESOURCE_SCOPE_ESCALATION")

    print("DELEGATED AUTHORITY ATTENUATION: 8/8 PASS")


if __name__ == "__main__":
    main()
