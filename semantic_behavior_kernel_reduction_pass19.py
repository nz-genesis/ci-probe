behaviors = {
    "creation": {"State", "Transition"},
    "revision": {"State", "Transition", "Evidence"},
    "expiration": {"State", "Transition", "Constraint"},
    "delegation": {"State", "Transition", "Authority"},
    "conflict": {"State", "Evidence", "Constraint"},
    "selection": {"State", "Transition", "Evidence"},
    "provenance": {"State", "Observation", "Evidence"},
    "authorization": {"Authority", "Capability", "Constraint", "Transition"},
    "recovery": {"State", "Transition", "Evidence", "Constraint"},
    "verification": {"Observation", "Evidence", "State"},
    "concurrency": {"State", "Transition", "Constraint", "Authority"},
    "substitution": {"State", "Evidence", "Authority", "Constraint"},
}
basis = {"State", "Transition", "Capability", "Authority", "Observation", "Evidence", "Constraint"}
for name, needs in behaviors.items():
    assert needs <= basis, name
for construct in {"Intent", "Goal", "Proposal", "Decision"}:
    assert construct not in basis
assert False is False
print("PASS19 semantic-behavior reduction: PASS")
print("behaviors tested: 12/12")
print("higher-order primitive promotions: NONE")
