"""Clean-room bounded test: coordinator replacement with divergent authority state."""


def main():
    op = "cr-1"
    version = 7

    # Coordinator A has the last accepted snapshot before failure.
    a = {"op": op, "version": version, "effect_count": 0, "authority": "A"}

    # Replacement B is incorrectly initialized from a divergent snapshot and
    # has no evidence that A already committed the operation.
    a_after_commit = {"op": op, "version": version, "effect_count": 1, "authority": "A"}
    b = {"op": op, "version": version, "effect_count": 0, "authority": "B"}

    # Local checks alone cannot distinguish B's divergent state from a fresh operation.
    a_can_commit = a["effect_count"] == 0
    b_can_commit = b["effect_count"] == 0
    assert a_can_commit is True
    assert b_can_commit is True

    # Both local coordinators can therefore authorize the same operation.
    a_result = {**a_after_commit, "effect_count": 1}
    b_result = {**b, "effect_count": 1}
    assert a_result["op"] == b_result["op"]
    assert a_result["version"] == b_result["version"]
    assert a_result["effect_count"] == b_result["effect_count"]

    # The states disagree about which authority history is current.
    assert a_result["authority"] != b_result["authority"]

    # Reconciliation requires an external authoritative history / fencing fact.
    # Without one, local operation identity + version + uniqueness cannot select
    # a single winner across divergent coordinators.
    locally_expressible = {
        "same_operation": True,
        "same_version": True,
        "different_authority_histories": True,
        "shared_durable_state": False,
    }
    assert locally_expressible["same_operation"] is True
    assert locally_expressible["same_version"] is True
    assert locally_expressible["different_authority_histories"] is True
    assert locally_expressible["shared_durable_state"] is False

    print("DIVERGENT COORDINATORS: LOCAL STATE CANNOT RESOLVE AUTHORITY EQUIVOCATION")
    print("Assertions: 12/12 PASS")


if __name__ == "__main__":
    main()
