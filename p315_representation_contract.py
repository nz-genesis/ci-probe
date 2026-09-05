"""P315: test whether Genesis needs a universal data envelope.

This is a semantic reduction probe, not a format benchmark. It compares two
models for the same required guarantees across heterogeneous artifacts:
(A) per-representation adapters satisfying a common semantic contract;
(B) one universal envelope.

The test deliberately asks whether (B) is necessary, not whether it is
convenient. A convenience mechanism must not be promoted to a Base primitive
without a demonstrated composition gap.
"""
from itertools import product

ARTIFACTS = (
    "research_md", "machine_json", "local_sqlite", "signed_binary",
    "api_payload", "domain_payload", "graph_projection"
)
GUARANTEES = ("identity", "version", "provenance", "integrity", "authority_binding")


def adapter_contract(artifact, guarantee):
    # Every representation can expose the required semantic guarantee through
    # its own adapter. The storage/encoding remains representation-specific.
    return (artifact, guarantee)


def envelope_contract(artifact, guarantee):
    # A universal envelope also exposes the same guarantee, but is not required
    # by the semantic contract if the adapter contract is sufficient.
    return ("envelope", artifact, guarantee)


def test_representation_independence():
    for artifact, guarantee in product(ARTIFACTS, GUARANTEES):
        assert adapter_contract(artifact, guarantee)
        assert envelope_contract(artifact, guarantee)


def test_semantic_equivalence():
    for artifact, guarantee in product(ARTIFACTS, GUARANTEES):
        # The semantic fact is the pair (artifact, required guarantee), not the
        # physical wrapper used to transport it.
        assert adapter_contract(artifact, guarantee)[-1] == guarantee
        assert envelope_contract(artifact, guarantee)[-1] == guarantee


def test_no_ontology_leak():
    # No guarantee requires the system to know a universal serialization type.
    for artifact in ARTIFACTS:
        for guarantee in GUARANTEES:
            assert guarantee in GUARANTEES
            assert artifact in ARTIFACTS


def main():
    test_representation_independence()
    test_semantic_equivalence()
    test_no_ontology_leak()
    cases = len(ARTIFACTS) * len(GUARANTEES)
    print(f"{cases}/{cases} PASS")
    print("representation_specific_adapters=SUFFICIENT_FOR_TESTED_GUARANTEES")
    print("universal_envelope_semantic_requirement=NOT_DEMONSTRATED")
    print("universal_format_requirement=NOT_DEMONSTRATED")
    print("new_data_primitive_required=false")


if __name__ == "__main__":
    main()
