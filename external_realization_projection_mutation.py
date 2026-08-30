"""Red-team mutation test for a public realization projection.

The experiment checks whether changes to private-only semantic fields can be
hidden by the current public projection. A collision is intentionally a
negative result: it means the projection alone cannot preserve that field's
semantics and therefore cannot be accepted as a sufficient contract boundary
without an additional semantic-preservation rule.
"""

from copy import deepcopy


PUBLIC_FIELDS = ("request_id", "operation", "key", "value", "constraint")


def project(request: dict) -> tuple:
    return tuple(request[field] for field in PUBLIC_FIELDS)


def run_mutations() -> dict[str, bool]:
    baseline = {
        "request_id": "p189-erb-001",
        "operation": "set",
        "key": "fixture",
        "value": "v1",
        "constraint": "deterministic",
        "authority": "delegated",
        "resource_version": "v1",
        "temporal_constraint": "window-A",
        "verification": "observed_value_equals_v1",
    }

    mutations = {
        "authority": "revoked",
        "resource_version": "v2",
        "temporal_constraint": "window-B",
        "verification": "different_condition",
    }

    results: dict[str, bool] = {}
    for field, value in mutations.items():
        mutated = deepcopy(baseline)
        mutated[field] = value
        results[field] = project(mutated) == project(baseline)

    assert all(results.values())
    return results


if __name__ == "__main__":
    results = run_mutations()
    print("projection mutation red-team: PASS (negative finding reproduced)")
    for field, collision in results.items():
        print(f"mutation={field} public_projection_unchanged={collision}")
