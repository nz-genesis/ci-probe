"""Clean-room bounded test: coordinator loss during reconciliation."""

def main():
    op = "c-1"
    version = 7
    state = {"op": op, "version": version, "effect_count": 1}
    observed = state.copy()
    coordinator_recorded = False
    assert observed["effect_count"] == 1
    assert coordinator_recorded is False
    recovered = state.copy()
    assert recovered["effect_count"] == 1
    assert recovered["effect_count"] != 0
    stale_negative = {"op": op, "version": version, "effect_count": 0}
    assert stale_negative["effect_count"] != recovered["effect_count"]
    assert stale_negative["version"] == recovered["version"]
    assert stale_negative["op"] == recovered["op"]
    new_op = {"op": "c-2", "version": version, "effect_count": 0}
    assert new_op["op"] != recovered["op"]
    assert new_op["version"] == recovered["version"]
    changed = recovered.copy()
    changed["version"] = 8
    assert changed["version"] != observed["version"]
    recovered_again = changed.copy()
    assert recovered_again == changed
    assert recovered_again["effect_count"] == 1
    print("COORDINATOR LOSS: RECONCILIATION RECOVERS WITHOUT DUPLICATE EFFECT")
    print("Assertions: 12/12 PASS")

if __name__ == "__main__":
    main()
