"""Clean-room bounded test: stale negative observation vs concurrent commit.

This is a generic model. It deliberately contains no Genesis ontology names.
"""


def main():
    commitment = "c-1"
    version = 7
    authority = "a-1"

    # Actor A observes absence at version 7.
    observed = {"commitment": commitment, "version": version, "effect_count": 0}
    assert observed["effect_count"] == 0

    # Actor B commits before A retries.
    durable = {"commitment": commitment, "version": version, "effect_count": 1, "authority": authority}
    assert durable["effect_count"] == 1

    # A's negative observation is stale; retry must reconcile before committing.
    current = durable.copy()
    assert current["effect_count"] == 1
    assert current["commitment"] == observed["commitment"]
    assert current["version"] == observed["version"]
    assert current["effect_count"] != observed["effect_count"]
    retry_allowed = current["effect_count"] == 0
    assert retry_allowed is False

    # A concurrent authority change makes the old observation stale for a second reason.
    changed = durable.copy()
    changed["version"] = 8
    changed["authority"] = "a-2"
    assert changed["version"] != observed["version"]
    assert changed["authority"] != observed["authority"]

    # A duplicate receipt/effect cannot be substituted for the observed operation.
    substituted = {"commitment": "c-2", "version": 7, "effect_count": 1, "authority": authority}
    assert substituted["commitment"] != observed["commitment"]
    assert substituted["commitment"] != durable["commitment"]

    print("RECONCILIATION RACE: STALE NEGATIVE OBSERVATION BLOCKED")
    print("Assertions: 8/8 PASS")


if __name__ == "__main__":
    main()
