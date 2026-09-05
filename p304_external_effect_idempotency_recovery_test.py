"""P304 bounded external-effect realization probe.

The probe separates Genesis local authorization safety from the external provider's
duplicate-effect semantics. Two attempts use one effect identity. Outcomes are
APPLIED, APPLIED_UNKNOWN, NOT_APPLIED_UNKNOWN, or REJECTED. Every permutation of the
eight lifecycle events and every pair of outcomes is explored.

Required result:
1. the governed commit predicate rejects every candidate whose authorization is stale;
2. an idempotent provider never creates duplicate external effects for one identity;
3. a non-idempotent provider admits a duplicate-effect witness under UNKNOWN+retry,
   demonstrating that exactly-once external side effects require provider cooperation,
   idempotency, or compensation rather than a new Genesis governance primitive.

This is a bounded executable model, not a distributed-systems proof.
"""
from itertools import permutations, product

ROOT = "R0"
EVENTS = ("AUTH", "ATTEMPT", "CRASH", "RECOVER", "OBSERVE", "RETRY", "COMMIT", "ROTATE")
OUTCOMES = ("APPLIED", "APPLIED_UNKNOWN", "NOT_APPLIED_UNKNOWN", "REJECTED")


def governed_commit_allowed(authorization, current_generation, observed, provider_effect):
    return (
        authorization == current_generation
        and current_generation == 1
        and authorization is not None
        and observed
        and provider_effect
    )


def simulate(order, outcomes, idempotent):
    current_generation = 1
    authorization = None
    provider_effect = False
    provider_count = 0
    observed = False
    stale_candidate_seen = False
    guard_accepted_stale = False
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
            naive_candidate = observed and provider_effect
            allowed = governed_commit_allowed(
                authorization, current_generation, observed, provider_effect
            )
            if naive_candidate and authorization != current_generation:
                stale_candidate_seen = True
                if allowed:
                    guard_accepted_stale = True

    return provider_count, stale_candidate_seen, guard_accepted_stale


def main():
    checked = 0
    stale_candidates = 0
    guard_accepted_stale = 0
    idempotent_duplicates = 0
    non_idempotent_duplicate_witness = False

    for order in permutations(EVENTS):
        for outcomes in product(OUTCOMES, repeat=2):
            count, stale_seen, stale_accepted = simulate(order, outcomes, idempotent=False)
            checked += 1
            stale_candidates += stale_seen
            guard_accepted_stale += stale_accepted
            if count > 1 and outcomes == ("APPLIED_UNKNOWN", "APPLIED"):
                non_idempotent_duplicate_witness = True

            idem_count, _, _ = simulate(order, outcomes, idempotent=True)
            if idem_count > 1:
                idempotent_duplicates += 1

    assert guard_accepted_stale == 0
    assert stale_candidates > 0
    assert idempotent_duplicates == 0
    assert non_idempotent_duplicate_witness
    print(
        "P304 exhaustive bounded external-effect cases: "
        f"{checked}/{checked} PASS; "
        f"stale-candidate cases={stale_candidates}; "
        "governed stale acceptance=0; idempotent duplicate count=0; "
        "non-idempotent duplicate witness PRESENT"
    )


if __name__ == "__main__":
    main()
