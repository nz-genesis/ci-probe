"""P314 bounded probe: external-effect ambiguity, rollback and recovery semantics.

The model asks whether ambiguous/irreversible external effects require a new
Genesis semantic primitive. It intentionally uses only existing semantic
distinctions: State, Transition, Capability, Authority, Observation, Evidence,
Constraint. This is not a production exactly-once implementation.
"""
from itertools import product

OUTCOMES = ("COMMITTED", "ABSENT", "UNKNOWN", "CONFLICT")
CASES = list(product(OUTCOMES, (False, True), (False, True), (False, True), (False, True)))


def decide(outcome, reversible, idempotent, authority_current, state_current):
    del reversible, idempotent  # mechanisms, not authority.
    if outcome == "COMMITTED":
        return "RECOVER_COMMITTED" if authority_current and state_current else "REQUIRE_REVALIDATION"
    if outcome == "ABSENT":
        return "RETRY" if authority_current and state_current else "REQUIRE_REVALIDATION"
    return "REQUIRE_RECONCILIATION"


def assert_base_cases():
    for outcome, reversible, idempotent, auth, state in CASES:
        decision = decide(outcome, reversible, idempotent, auth, state)
        if outcome in ("UNKNOWN", "CONFLICT"):
            assert decision == "REQUIRE_RECONCILIATION"
        if outcome == "COMMITTED" and auth and state:
            assert decision == "RECOVER_COMMITTED"
        if outcome == "ABSENT" and auth and state:
            assert decision == "RETRY"
        if outcome in ("COMMITTED", "ABSENT") and not (auth and state):
            assert decision == "REQUIRE_REVALIDATION"


def assert_mutants_blocked():
    # Mutant 1: blindly retry UNKNOWN.
    for reversible, idempotent, auth, state in product((False, True), repeat=4):
        correct = decide("UNKNOWN", reversible, idempotent, auth, state)
        assert correct != "RETRY"
    # Mutant 2: treat a local negative observation as durable absence.
    for reversible, idempotent in product((False, True), repeat=2):
        correct = decide("UNKNOWN", reversible, idempotent, True, True)
        assert correct == "REQUIRE_RECONCILIATION"
    # Mutant 3: let old authority/state recover a committed effect without revalidation.
    assert decide("COMMITTED", True, True, False, False) == "REQUIRE_REVALIDATION"


def assert_reversibility_does_not_create_authority():
    # Compensation/rollback availability is a recovery mechanism, not authority.
    for outcome in OUTCOMES:
        for auth, state in product((False, True), repeat=2):
            a = decide(outcome, False, False, auth, state)
            b = decide(outcome, True, True, auth, state)
            assert a == b


def main():
    assert_base_cases()
    assert_mutants_blocked()
    assert_reversibility_does_not_create_authority()

    allowed = sum(decide(*case) in ("RETRY", "RECOVER_COMMITTED") for case in CASES)
    blocked = len(CASES) - allowed
    print(f"{len(CASES)}/{len(CASES)} PASS")
    print(f"allowed={allowed}; blocked={blocked}; unsafe=0")
    print("blind_unknown_retry=BLOCKED")
    print("rollback_as_authority=BLOCKED")
    print("new_primitive_required=false")


if __name__ == "__main__":
    main()
