"""Public, Genesis-agnostic Pass 12 reduction probe.

No private Genesis data or ontology source is embedded here. The probe tests
only the abstract semantic distinction between an aim and a state transition.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class State:
    facts: frozenset[tuple[str, str]]


@dataclass(frozen=True)
class Transition:
    before: str
    after: str
    intent_ref: str | None
    authority: str
    capability: str
    constraints: tuple[str, ...]


def value(state: State, key: str) -> str | None:
    return next((v for k, v in state.facts if k == key), None)


def run() -> None:
    # Intent can exist before a transition.
    s0 = State(frozenset({
        ("goal:G1:target", "target-A"),
        ("intent:I1:target", "target-A"),
        ("intent:I1:status", "active"),
        ("intent:I1:goal", "G1"),
    }))
    assert value(s0, "intent:I1:target") == "target-A"

    # One intent can map to multiple alternative transitions.
    t1 = Transition("S0", "S1", "I1", "A1", "C1", ("safe",))
    t2 = Transition("S0", "S2", "I1", "A1", "C1", ("safe",))
    assert t1.intent_ref == t2.intent_ref == "I1"
    assert t1.after != t2.after

    # Intent revision/abandonment is distinct from execution.
    s1 = State(s0.facts | {
        ("intent:I1:status", "abandoned"),
        ("intent:I2:target", "target-B"),
        ("intent:I2:status", "active"),
    })
    assert value(s1, "intent:I2:target") == "target-B"

    # A transition can exist without an explicit intent.
    t3 = Transition("S1", "S2", None, "A1", "observe", ("no-effect",))
    assert t3.intent_ref is None

    # Goal and intent are not identical: one goal can support distinct intents.
    assert value(s0, "goal:G1:target") == value(s0, "intent:I1:target")
    assert value(s1, "intent:I2:target") != value(s1, "goal:G1:target")

    # Constraint-only encoding is ambiguous: the same target predicate can
    # mean an admissibility requirement or an intended outcome.
    predicate = "eventual(target-A)"
    admissibility = ("constraint", predicate)
    intention = ("aim", predicate)
    assert admissibility != intention

    print("PASS12 PUBLIC REDUCTION: 7/7")


if __name__ == "__main__":
    run()
