"""P191 bounded probe: ambiguity must not be collapsed by authority or confidence."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    name: str
    confidence: float
    authorized: bool


@dataclass(frozen=True)
class Action:
    name: str
    reversible: bool
    safe_for_all_candidates: bool = False


def govern(candidates, action, observation_available=False, hitl=False):
    """Return a bounded governance outcome without treating authority as truth."""
    unique = len(candidates) == 1
    uniquely_authorized = unique and candidates[0].authorized

    if uniquely_authorized:
        return "EXECUTE"
    if observation_available:
        return "OBSERVE_FIRST"
    if hitl:
        return "HITL"
    if action.reversible and action.safe_for_all_candidates and candidates:
        return "SAFE_REVERSIBLE"
    return "NO_EXECUTION"


def assert_case(label, got, expected):
    assert got == expected, f"{label}: expected {expected}, got {got}"


def main():
    a = Candidate("A", 0.95, True)
    x = Candidate("X", 0.99, True)
    y = Candidate("Y", 0.10, True)
    unauthorized = Candidate("U", 0.99, False)

    assert_case("unique authorized", govern([a], Action("write", False)), "EXECUTE")
    assert_case("ambiguous reversible but not universally safe", govern([x, y], Action("probe", True)), "NO_EXECUTION")
    assert_case("ambiguous reversible universally safe", govern([x, y], Action("observe", True, True)), "SAFE_REVERSIBLE")
    assert_case("ambiguous irreversible", govern([x, y], Action("delete", False)), "NO_EXECUTION")
    assert_case("observation available", govern([x, y], Action("delete", False), observation_available=True), "OBSERVE_FIRST")
    assert_case("HITL", govern([x, y], Action("delete", False), hitl=True), "HITL")
    assert_case("confidence is not authority", govern([x, y], Action("delete", False)), "NO_EXECUTION")
    assert_case("unauthorized alternative preserves ambiguity", govern([a, unauthorized], Action("write", False)), "NO_EXECUTION")
    assert_case("high confidence does not override material ambiguity", govern([x, y], Action("delete", False)), "NO_EXECUTION")
    print("AMBIGUITY GOVERNED ACTION: 9/9 PASS")


if __name__ == "__main__":
    main()
