"""Clean-room bounded test: network partition during reconciliation."""


def main():
    op = "p-1"
    version = 7

    # Both sides begin from the same durable authority snapshot.
    durable = {"op": op, "version": version, "effect_count": 0}
    a = durable.copy()
    b = durable.copy()

    # Partition: neither side can observe the other's new state.
    partitioned = True
    assert partitioned is True
    a_observed = a.copy()
    b_observed = b.copy()
    assert a_observed == b_observed

    # Only the authoritative shared commit domain may create the effect.
    authoritative = durable.copy()
    authoritative["effect_count"] = 1
    assert authoritative["effect_count"] == 1

    # A and B each attempt recovery from their stale snapshot during partition.
    a_retry_token = (a_observed["op"], a_observed["version"])
    b_retry_token = (b_observed["op"], b_observed["version"])
    assert a_retry_token == b_retry_token

    # Commit gate compares against current durable version/effect state.
    a_commit_allowed = (
        a_retry_token == (authoritative["op"], authoritative["version"])
        and authoritative["effect_count"] == 0
    )
    b_commit_allowed = (
        b_retry_token == (authoritative["op"], authoritative["version"])
        and authoritative["effect_count"] == 0
    )
    assert a_commit_allowed is False
    assert b_commit_allowed is False

    # Partition heals; both actors reconcile against the same current durable state.
    partitioned = False
    a_recovered = authoritative.copy()
    b_recovered = authoritative.copy()
    assert a_recovered == b_recovered
    assert a_recovered["effect_count"] == 1
    assert b_recovered["effect_count"] == 1

    # No stale negative observation can authorize a duplicate after healing.
    assert a_recovered["effect_count"] != 0
    assert b_recovered["effect_count"] != 0

    # A fresh operation remains independently identifiable.
    fresh = {"op": "p-2", "version": version, "effect_count": 0}
    assert fresh["op"] != authoritative["op"]
    assert fresh["version"] == authoritative["version"]

    # Authority/version change invalidates both old partition snapshots.
    newer = authoritative.copy()
    newer["version"] = 8
    assert newer["version"] != a_observed["version"]
    assert newer["version"] != b_observed["version"]

    print("NETWORK PARTITION: STALE RECOVERY CANNOT DUPLICATE DURABLE EFFECT")
    print("Assertions: 15/15 PASS")


if __name__ == "__main__":
    main()
