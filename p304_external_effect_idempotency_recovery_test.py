"""P304 bounded external-effect realization probe.

The probe separates Genesis local authorization safety from the external provider's
duplicate-effect semantics. Two attempts use one effect identity. Outcomes are
APPLIED, APPLIED_UNKNOWN, NOT_APPLIED_UNKNOWN, or REJECTED. Every permutation of the
eight lifecycle events and every pair of outcomes is explored.

Required result:
1. local COMMIT is never accepted without current protected authorization and an
   authoritative observed external effect;
2. an idempotent provider never creates duplicate external effects for one identity;
3. a non-idempotent provider admits duplicate external effects under UNKNOWN+retry,
   demonstrating that exactly-once external side effects require provider cooperation,
   idempotency, or compensation rather than a new Genesis governance primitive.

This is a bounded executable model, not a distributed-systems proof.
"""
from itertools import permutations, product

ROOT = "R0"
EVENTS = ("AUTH", "ATTEMPT", "CRASH", "RECOVER", "OBSERVE", "RETRY", "COMMIT", "ROTATE")
OUTCOMES = ("APPLIED", "APPLIED_UNKNOWN", "NOT_APPLIED_UNKNOWN", "REJECTED")


def simulate(order, outcomes, idempotent):
    current_generation = 1
    authorization = None
    provider_effect = False
    provider_count = 0
    observed = False
    committed = False
    outcome_index = 0

    for event in order:
        if event == "AUTH":
            authorization = current_generation
        elif event == "ROTATE":
            current_generation += 1
        elif event in ("ATTEMPT", "RETRY"):
            outcome = outcomes[outcome_index]
            outcome_index += 1
            if not (idempotent and provider_effect):
                if outcome in ("APPLIED", "APPLIED_UNKNOWN"):
                    provider_count += 1
                    provider_effect = True
            if outcome == "APPLIED":
                observed = True
            elif outcome in ("APPLIED_UNKNOWN", "NOT_APPLIED_UNKNOWN"):
                observed = False
        elif event == "CRASH":
            observed = False
        elif event == "RECOVER":
            pass
        elif event == "OBSERVE":
            observed = provider_effect
        elif event == "COMMIT":
            if (
                authorization == current_generation
                and current_generation == 1
                and authorization is not None
                and authorization >= 0
                and observed
                and provider_effect
            ):
                committed = True

    local_commit_safe = (
        not committed
        or (
            authorization == current_generation
            and current_generation == 1
            and observed
            and provider_effect
        )
    )
    return local_commit_safe, provider_count


def main():
    checked = 0
    unsafe_local_commits = 0
    non_idempotent_duplicate_witness = False
    idempotent_duplicates = 0

    for order in permutations(EVENTS):
        for outcomes in product(OUTCOMES, repeat=2):
            safe, count = simulate(order, outcomes, idempotent=False)
            checked += 1
            if not safe:
                unsafe_local_commits += 1
            if count > 1 and outcomes == ("APPLIED_UNKNOWN", "APPLIED"):
                non_idempotent_duplicate_witness = True

            _, idem_count = simulate(order, outcomes, idempotent=True)
            if idem_count > 1:
                idempotent_duplicates += 1

    assert unsafe_local_commits == 0
    assert idempotent_duplicates == 0
    assert non_idempotent_duplicate_witness
    print(
        "P304 exhaustive bounded external-effect cases: "
        f"{checked}/{checked} PASS; "
        "local commit guard PASS; idempotent provider duplicate guard PASS; "
        "non-idempotent duplicate witness PRESENT"
    )


if __name__ == "__main__":
    main()
