# Dynamic delegation experiment

## Scope

Clean-room continuation of the authority/HITL research. It extends the previous single authority boundary to a two-hop delegation chain and tests revocation at either edge.

## Contract

For an irreversible proposal, the complete active delegation chain must be valid at the realization boundary.

## Mechanisms

- `stale-delegation-chain` — relies on authority validity captured at request time;
- `revalidate-delegation-chain` — validates every delegation edge at realization time.

## Results

| Case | Stale chain | Revalidated chain |
|---|---|---|
| stable chain | EXECUTED | EXECUTED |
| root revokes agent before realization | EXECUTED | BLOCKED_REVOKED |
| agent→executor delegation revoked before realization | EXECUTED | BLOCKED_REVOKED |
| acknowledgement/evidence lost after effect | UNKNOWN | UNKNOWN |

## Discriminating result

The authority requirement propagates through the entire delegation chain. A realization strategy using stale authority state can produce an effect that violates the temporal authority contract.

The semantic requirement is naturally described as:

```text
active delegation graph
+ validity/revocation state
+ realization-boundary constraint
→ admission / rejection
```

No new authority engine, action primitive, execution primitive, HITL primitive, or delegation primitive is required by this bounded model.

## Important distinction

The result does not prove that a distributed authority graph can always be checked atomically. It only establishes the semantic requirement that stale delegation is not equivalent to currently valid authority when the contract requires current authorization.

## Epistemic status

`OBSERVED / BOUNDED EXPERIMENT`.

## Public boundary

No Genesis source, private architecture, credentials, internal endpoints, datasets or canonical decisions are included. Interpretation remains in private `genesis-lab`.
