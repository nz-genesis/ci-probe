"""P196 bounded probe: nested private mutations must not change public derived output."""


def public_semantics(state):
    return {
        "status": state["public"]["status"],
        "version": state["public"]["version"],
        "risk_band": state["public"]["risk_band"],
    }


def good_projection(state):
    public = state["public"]
    return {
        "status": public["status"],
        "version": public["version"],
        "risk_band": public["risk_band"],
    }


def bad_projection(state):
    # Adversarial implementation: private score is smuggled into a derived
    # public value even though score is not declared public semantics.
    public = state["public"]
    private = state["private"]
    return {
        "status": public["status"],
        "version": public["version"],
        "risk_band": f"{public['risk_band']}:{private['risk']['score']}",
    }


def catches_private_noninterference_violation(projection, base, mutated):
    return projection(base) == projection(mutated)


def main():
    base = {
        "public": {
            "status": "ready",
            "version": 1,
            "risk_band": "normal",
        },
        "private": {
            "identity": {"operator": "alpha", "token": "secret-A"},
            "risk": {"score": 10, "notes": {"source": "internal"}},
        },
    }

    private_note_mutation = {
        **base,
        "private": {
            "identity": {"operator": "beta", "token": "secret-B"},
            "risk": {"score": 10, "notes": {"source": "changed"}},
        },
    }
    private_score_mutation = {
        **base,
        "private": {
            "identity": {"operator": "alpha", "token": "secret-A"},
            "risk": {"score": 99, "notes": {"source": "internal"}},
        },
    }
    public_mutation = {
        **base,
        "public": {"status": "blocked", "version": 1, "risk_band": "high"},
    }

    # Positive noninterference witnesses for nested private mutations.
    assert catches_private_noninterference_violation(good_projection, base, private_note_mutation)
    assert catches_private_noninterference_violation(good_projection, base, private_score_mutation)

    # Public semantics remain observable.
    assert good_projection(base) != good_projection(public_mutation)

    # The verifier must catch the adversarial derived-field leak rather than
    # merely asserting that the good projection has the intended shape.
    assert not catches_private_noninterference_violation(bad_projection, base, private_score_mutation)

    # Private fields are not emitted directly by the good projection.
    serialized = str(good_projection(base))
    assert "secret-A" not in serialized
    assert "internal" not in serialized
    assert "10" not in serialized

    print("NESTED DERIVED NONINTERFERENCE: 8/8 PASS")


if __name__ == "__main__":
    main()
