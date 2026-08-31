"""P194 bounded probe: projection collisions must block projection-only action."""

PUBLIC_FIELDS = ("request_id", "operation", "key", "value", "constraint")


def project(request):
    return tuple(request[field] for field in PUBLIC_FIELDS)


def projection_only_decision(request, baseline_projection):
    if project(request) != baseline_projection:
        return "REJECT"
    # A projection collision proves that private decision-relevant state is
    # not represented. Projection-only execution therefore requires refresh.
    return "REQUIRE_REVALIDATION"


def full_state_decision(request):
    if request["authority"] != "delegated":
        return "UNAUTHORIZED"
    if request["resource_version"] != "v1":
        return "STALE"
    if request["temporal_constraint"] != "window-A":
        return "OUTSIDE_WINDOW"
    if request["verification"] != "observed_value_equals_v1":
        return "UNVERIFIED"
    return "EXECUTE"


def main():
    baseline = {
        "request_id": "p194-001",
        "operation": "set",
        "key": "fixture",
        "value": "v1",
        "constraint": "deterministic",
        "authority": "delegated",
        "resource_version": "v1",
        "temporal_constraint": "window-A",
        "verification": "observed_value_equals_v1",
    }
    baseline_projection = project(baseline)

    mutations = [
        ("authority revoked", {"authority": "revoked"}, "UNAUTHORIZED"),
        ("resource version changed", {"resource_version": "v2"}, "STALE"),
        ("temporal constraint changed", {"temporal_constraint": "window-B"}, "OUTSIDE_WINDOW"),
        ("verification condition changed", {"verification": "different_condition"}, "UNVERIFIED"),
    ]

    assert projection_only_decision(baseline, baseline_projection) == "REQUIRE_REVALIDATION"
    assert full_state_decision(baseline) == "EXECUTE"

    for label, mutation, expected_full in mutations:
        mutated = dict(baseline)
        mutated.update(mutation)
        assert project(mutated) == baseline_projection, f"{label}: expected projection collision"
        assert projection_only_decision(mutated, baseline_projection) == "REQUIRE_REVALIDATION", label
        assert full_state_decision(mutated) == expected_full, label

    print("PROJECTION COLLISION GOVERNED ACTION: 10/10 PASS")


if __name__ == "__main__":
    main()
