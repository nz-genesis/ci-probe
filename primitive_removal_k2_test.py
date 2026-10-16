from primitive_removal_k2 import CASES, invariant_holds, preserve_distinction, no_covert_primitive, verify


def test_k2_verifies():
    verify()


def test_all_candidate_distinctions_survive_generic_representation():
    assert all(preserve_distinction(case) for case in CASES)


def test_no_case_introduces_named_primitive():
    assert all(no_covert_primitive(case) for case in CASES)


def test_constraint_invariant_is_not_reduced_to_information_presence():
    case = next(case for case in CASES if case.candidate == "constraint")
    assert invariant_holds(case, case.left, "left")
    assert not invariant_holds(case, case.right, "right")
