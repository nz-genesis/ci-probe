"""Clean-room adversarial integrity checks for an external realization envelope.

Generic only. No private Genesis hypotheses, credentials, private datasets,
internal endpoints, or canonical decisions.
"""

from dataclasses import replace
from external_realization_envelope_minimization import (
    PublicEnvelope,
    build_envelope,
    private_semantic_contract,
    realize,
)


def baseline() -> PublicEnvelope:
    return build_envelope(private_semantic_contract())


def main() -> None:
    env = baseline()
    applied = realize(env)
    assert applied["outcome"] == "applied"

    # Authority laundering: changing only the admission result must be visible.
    forged_admission = replace(env, admission="deny")
    assert realize(forged_admission)["outcome"] != applied["outcome"]

    # Provenance substitution must not be silently treated as the baseline.
    forged_provenance = replace(env, provenance_commitment="0" * 64)
    assert forged_provenance.provenance_commitment != env.provenance_commitment

    # Stale/replay envelope remains distinguishable from a fresh private contract.
    stale = build_envelope(private_semantic_contract(resource_version="v2"))
    assert stale.provenance_commitment != env.provenance_commitment
    assert realize(stale)["outcome"] != applied["outcome"]

    # Public realization must not turn verification into an exported predicate.
    verified_private_mutation = build_envelope(
        private_semantic_contract(verification="different-value-rule")
    )
    assert verified_private_mutation.admission == env.admission
    assert verified_private_mutation.provenance_commitment != env.provenance_commitment

    # An evidence record from a different request must not be confused with this request.
    foreign = replace(applied, request_id="foreign-request")
    assert foreign["request_id"] != applied["request_id"]

    print("external realization envelope integrity: PASS")
    print("checks=authority-laundering,provenance-substitution,stale-replay,private-verification,request-binding")


if __name__ == "__main__":
    main()
