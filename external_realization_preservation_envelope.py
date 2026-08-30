"""Bounded clean-room test for a minimal semantic-preservation envelope.

The previous projection deliberately omitted material dimensions and therefore
collapsed authority, version, temporal, and verification mutations. This probe
asks a narrower question: can those dimensions be carried generically, without
Genesis-specific vocabulary, and can omission of each dimension be detected?

This is evidence about a generic boundary mechanism, not Genesis ontology.
"""
from dataclasses import dataclass, replace
from hashlib import sha256


@dataclass(frozen=True)
class Envelope:
    request_id: str
    predecessor: str
    operation_code: int
    resource_version: int
    authority_min: int
    authority_max: int
    observed_epoch: int
    verification_code: int
    expected_value: int
    irreversible: bool


def digest(e: Envelope) -> str:
    payload = "|".join(str(v) for v in e.__dict__.values())
    return sha256(payload.encode()).hexdigest()


def realize(e: Envelope) -> tuple[str, int, str]:
    authority_ok = e.authority_min <= e.observed_epoch <= e.authority_max
    verified = e.expected_value == 42
    applied = authority_ok and verified and e.resource_version == 7
    outcome = "applied" if applied else "rejected"
    observed = 42 if applied else 0
    return outcome, observed, digest(e)


def base() -> Envelope:
    return Envelope("opaque-01", "opaque-parent", 1, 7, 10, 20, 15, 3, 42, True)


def mutation_suite() -> dict[str, bool]:
    b = base()
    mutations = {
        "resource_version": replace(b, resource_version=8),
        "authority_window": replace(b, authority_min=16, authority_max=20),
        "observed_epoch": replace(b, observed_epoch=21),
        "verification_target": replace(b, expected_value=41),
        "irreversibility": replace(b, irreversible=False),
        "predecessor": replace(b, predecessor="opaque-other"),
    }
    results = {}
    baseline = realize(b)
    for name, mutated in mutations.items():
        result = realize(mutated)
        # Every tested dimension must at least change the envelope digest.
        # Dimensions that affect admissibility/verification must also change outcome.
        digest_changed = result[2] != baseline[2]
        outcome_changed = result[0] != baseline[0]
        required_outcome_change = name in {
            "resource_version", "authority_window", "observed_epoch", "verification_target"
        }
        results[name] = digest_changed and (outcome_changed if required_outcome_change else True)
    assert all(results.values())
    return results


def ablation_suite() -> dict[str, bool]:
    b = base()
    # Each pair differs in exactly one material dimension. Removing that
    # dimension from a hypothetical projection makes the pair collide.
    pairs = {
        "resource_version": replace(b, resource_version=8),
        "authority_window": replace(b, authority_min=16, authority_max=20),
        "observed_epoch": replace(b, observed_epoch=21),
        "verification_target": replace(b, expected_value=41),
    }
    fields = {
        "resource_version", "authority_min", "authority_max", "observed_epoch", "expected_value"
    }
    results = {}
    for name, mutated in pairs.items():
        omitted = fields - {
            "resource_version" if name == "resource_version" else "authority_min" if name == "authority_window" else "observed_epoch" if name == "observed_epoch" else "expected_value"
        }
        # The full envelope distinguishes the pair; an ablation that removes
        # the mutated dimension must not be accepted as preserving semantics.
        def projected(x: Envelope) -> tuple:
            values = []
            for field in fields:
                if field not in omitted:
                    values.append(getattr(x, field))
            return tuple(values)
        # Deliberately assert the opposite: omitted material field collapses.
        results[name] = projected(b) == projected(mutated)
    assert all(results.values())
    return results


if __name__ == "__main__":
    mutations = mutation_suite()
    ablations = ablation_suite()
    print("PRESERVATION ENVELOPE MUTATION: PASS")
    print("PRESERVATION ENVELOPE ABLATION: PASS (negative finding reproduced)")
    print("mutation_results", mutations)
    print("ablation_collisions", ablations)
    print("baseline", realize(base()))
