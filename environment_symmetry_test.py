from environment_symmetry import CONTRACT, ENVIRONMENTS, run


def test_contract_is_environment_independent():
    results = run()
    assert len(results) == len(ENVIRONMENTS) == 10
    assert {r.admitted for r in results} == {True}
    assert {r.verified for r in results} == {True}
    assert {r.final_state for r in results} == {{"value": 1}}
    assert {r.effect_key for r in results} == {CONTRACT.effect_key}


def test_precondition_blocks_same_contract_after_state_change():
    for environment in ENVIRONMENTS:
        result = environment.realize(CONTRACT, {"value": 1})
        assert result.admitted is False
        assert result.verified is False
        assert result.final_state == {"value": 1}


def test_environment_identity_does_not_change_semantic_outcome():
    results = run()
    for result in results:
        assert result.final_state["value"] == 1
        assert result.effect_key == CONTRACT.effect_key
