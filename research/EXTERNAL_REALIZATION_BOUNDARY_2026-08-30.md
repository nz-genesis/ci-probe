# External Realization Boundary — Clean-Room Experiment

## Scope

This is a generic executable experiment. It is not part of Genesis architecture and contains no private Genesis hypotheses, credentials, internal endpoints, private datasets, or canonical decisions.

## Question

Can an explicitly allow-listed generic contract be projected from a richer internal request, realized by independent mechanisms, and produce matching observable evidence without carrying non-public fields across the boundary?

## Test

`external_realization_boundary.py`:

1. constructs a generic request containing both public-safe fields and deliberately non-public fields;
2. projects only the allow-listed public contract;
3. realizes that public contract using two independent mechanisms (direct and queued);
4. compares outcome, observed value, request identity, and contract digest;
5. asserts that forbidden fields do not cross the projection boundary.

## Interpretation boundary

The experiment proves only generic boundary behavior. Its result must not be interpreted as proof of Genesis semantics. Private Genesis may consume the result as evidence only after independently verifying that an actual private contract can be projected without semantic loss or unacceptable leakage.

## Required follow-up

A private-side provenance mechanism must establish correspondence between a real private semantic contract and its public projection without publishing the private contract itself. The correspondence must then be subjected to Red Team review before any canonical Genesis impact.
