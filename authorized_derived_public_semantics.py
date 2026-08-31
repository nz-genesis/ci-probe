"""P197 bounded probe: only declared, authorized private→public derivation may be observable."""


def project(state):
    public = state["public"]
    contract = state["contract"]
    private = state["private"]
    result = {"status": public["status"], "version": public["version"]}
    if contract["risk_dependency"] and contract["risk_publication_authorized"]:
        result["risk_band"] = "high" if private["risk"]["score"] >= 80 else "normal"
    return result


def equivalent_under_contract(left, right):
    return project(left) == project(right)


def main():
    contract = {"risk_dependency": False, "risk_publication_authorized": False}
    base = {
        "public": {"status": "ready", "version": 1},
        "private": {"risk": {"score": 10, "notes": {"source": "internal-A"}}},
        "contract": contract,
    }
    private_changed = {
        "public": {"status": "ready", "version": 1},
        "private": {"risk": {"score": 99, "notes": {"source": "internal-B"}}},
        "contract": contract,
    }

    # Without an explicit public semantic dependency, private states are
    # observationally equivalent at the public boundary.
    assert equivalent_under_contract(base, private_changed)

    # Declaring a dependency is not sufficient by itself: publication also
    # requires explicit authority.
    dependency_only = {**base, "contract": {"risk_dependency": True, "risk_publication_authorized": False}}
    dependency_only_changed = {**private_changed, "contract": dependency_only["contract"]}
    assert equivalent_under_contract(dependency_only, dependency_only_changed)

    # Once the dependency is both declared and authorized, the private value
    # is intentionally part of the public semantic contract and is observable.
    authorized_contract = {"risk_dependency": True, "risk_publication_authorized": True}
    authorized_low = {**base, "contract": authorized_contract}
    authorized_high = {**private_changed, "contract": authorized_contract}
    assert not equivalent_under_contract(authorized_low, authorized_high)
    assert project(authorized_low)["risk_band"] == "normal"
    assert project(authorized_high)["risk_band"] == "high"

    # Adversarial contract: an unauthorized dependency must not be smuggled in
    # by an implementation that ignores the contract.
    def unsafe_project(state):
        return {"status": state["public"]["status"], "version": state["public"]["version"],
                "risk_band": "high" if state["private"]["risk"]["score"] >= 80 else "normal"}

    assert unsafe_project(dependency_only) != unsafe_project(dependency_only_changed)
    assert project(dependency_only) == project(dependency_only_changed)

    # Public mutations remain observable regardless of private equivalence.
    public_changed = {**base, "public": {"status": "blocked", "version": 1}}
    assert not equivalent_under_contract(base, public_changed)

    print("AUTHORIZED DERIVED PUBLIC SEMANTICS: 8/8 PASS")


if __name__ == "__main__":
    main()
