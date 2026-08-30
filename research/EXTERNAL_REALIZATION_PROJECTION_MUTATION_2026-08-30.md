# External Realization Projection Mutation — Clean-Room Red Team

## Question

Does the current allow-listed public projection preserve private-only semantic dimensions?

## Test

Mutate one private-only field at a time while holding all public fields constant:

- authority;
- resource version;
- temporal constraint;
- verification condition.

Compare the resulting public projection with the baseline projection.

## Expected negative result

If a private-only mutation leaves the public projection identical, the projection is not sufficient to represent that private dimension. This is a red-team finding, not a CI failure.

## Boundary

This experiment is generic and contains no private Genesis contract, credentials, private endpoints, datasets, or canonical decisions. Its result must be interpreted only as a statement about the projection function used by this clean-room experiment.
