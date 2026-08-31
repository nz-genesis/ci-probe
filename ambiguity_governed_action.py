"""P191 bounded probe: ambiguity must not be silently collapsed into authority."""
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


def govern(candidates, action, observation_available=False, hitl=False):
    authorized = [c for c in candidates if c.authorized]
    unique = len(authorized) == 1
    if unique:
        return "EXECUTE"
    if observation_available:
        return "OBSERVE_FIRST"
    if hitl:
        return "HITL"
    if action.reversible and len(authorized) > 0:
        return "HOLD_OR_SAFE_REVERSIBLE"
    return "NO_EXECUTION"


def assert_case(label, got, expected):
    assert got == expected, f"{label}: expected {expected}, got {got}"


def main():
    a = Candidate("A", 0.95, True)
    b = Candidate("B", 0.05, False)
    x = Candidate("X", 0.91, True)
    y = Candidate("Y", 0.89, True)

    assert_case("unique authorized", govern([a], Action("write", False)), "EXECUTE")
    assert_case("ambiguous reversible", govern([x, y], Action("probe", True)), "HOLD_OR_SAFE_REVERSIBLE")
    assert_case("ambiguous irreversible", govern([x, y], Action("delete", False)), "NO_EXECUTION")
    assert_case("observation available", govern([x, y], Action("delete", False), observation_available=True), "OBSERVE_FIRST")
    assert_case("HITL", govern([x, y], Action("delete", False), hitl=True), "HITL")
    assert_case("confidence is not authority", govern([a, b], Action("delete", False)), "EXECUTE")
    assert_case("no authorized interpretation", govern([Candidate("N", .99, False), Candidate("M", .98, False)], Action("probe", True)), "NO_EXECUTION")
    assert_case("high confidence does not override ambiguity", govern([x, y], Action("delete", False)), "NO_EXECUTION")
    print("AMBIGUITY GOVERNED ACTION: 8/8 PASS")

if __name__ == "__main__":
    main()
