"""Clean-room primitive-removal experiment.

The previous experiment established that at-most-once effect can be a semantic
contract requirement. This pass removes any named idempotency construct and
represents the requirement only as a constraint over request identity and
transition/effect behavior. A counterfactual without that constraint is also
executed to expose the semantic loss caused by removing the guarantee itself.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Request:
    request_id: str
    value: str


@dataclass(frozen=True)
class Constraint:
    max_effects_per_request: int | None


@dataclass(frozen=True)
class State:
    value: str | None
    effect_count: int
    applied_request_ids: tuple[str, ...]


REQUEST = Request("req-001", "v1")
AT_MOST_ONCE = Constraint(max_effects_per_request=1)
NO_EFFECT_CARDINALITY_CONSTRAINT = Constraint(max_effects_per_request=None)


def apply_transition(
    state: State,
    request: Request,
    constraint: Constraint,
) -> State:
    """Represent the guarantee without a named idempotency primitive."""
    if (
        constraint.max_effects_per_request is not None
        and request.request_id in state.applied_request_ids
    ):
        return state

    return State(
        value=request.value,
        effect_count=state.effect_count + 1,
        applied_request_ids=state.applied_request_ids + (request.request_id,),
    )


def run_two_attempts(constraint: Constraint) -> State:
    state = State(value=None, effect_count=0, applied_request_ids=())
    state = apply_transition(state, REQUEST, constraint)
    state = apply_transition(state, REQUEST, constraint)
    return state


def verify() -> None:
    constrained = run_two_attempts(AT_MOST_ONCE)
    unconstrained = run_two_attempts(NO_EFFECT_CARDINALITY_CONSTRAINT)

    # Final-state semantics survive removal of a named idempotency construct.
    assert constrained.value == unconstrained.value == "v1"

    # The at-most-once guarantee survives as an ordinary constraint.
    assert constrained.effect_count == 1
    assert constrained.applied_request_ids == ("req-001",)

    # Removing the guarantee itself creates a real semantic loss.
    assert unconstrained.effect_count == 2
    assert unconstrained.applied_request_ids == ("req-001", "req-001")

    assert constrained.effect_count < unconstrained.effect_count


if __name__ == "__main__":
    verify()
    print("primitive removal: PASS")
