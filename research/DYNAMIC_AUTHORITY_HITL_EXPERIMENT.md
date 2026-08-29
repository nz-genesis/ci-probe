# Dynamic authority × HITL × irreversibility experiment

## Scope

Clean-room continuation after the first HITL boundary pass. This experiment deliberately combines unresolved dimensions instead of repeating static HITL examples:

- human approval;
- authority revocation after approval;
- irreversible realization boundary;
- late acknowledgement/evidence loss.

## Contract

An irreversible proposal may be realized only if the required authority is valid **at the realization boundary**, not merely when the request was issued or approved.

## Realization mechanisms

1. `snapshot-authority` — remembers authority from request time.
2. `revalidate-at-realization` — checks authority again immediately before realization.

## Discriminating case

Request `req-002`:

- authority valid at request time;
- human approval obtained;
- authority revoked before realization;
- irreversible effect requested.

Observed:

| Mechanism | Result | Effect |
|---|---|---:|
| snapshot-authority | executed | 1 |
| revalidate-at-realization | blocked-revoked | 0 |

The two mechanisms are therefore **not semantically equivalent** for the stronger contract.

## Interpretation

This is a useful boundary result. It does **not** show that realization mechanism is a Genesis primitive. It shows that the semantic contract contains a temporal authority requirement:

```text
authority validity
       @ realization boundary
       ↓
permission for irreversible transition
```

A realization mechanism that does not satisfy that constraint is semantically non-conforming.

The same result is naturally expressible through authority state + validity/revocation constraint + transition admission + evidence. No dedicated `Action`, `Execution`, `HITL`, or `AuthorityEngine` primitive is demonstrated.

## Additional cases

- stable authority + approval → both mechanisms execute;
- approval absent → pending-human, no effect;
- effect occurred but acknowledgement/observation is absent → UNKNOWN/reconciliation-required.

## Important result

Human approval does **not** freeze authority. Approval and authority validity are separate dimensions.

Likewise, revocation before realization is different from revocation after effect. The latter cannot be used to infer absence of external effect and remains an evidence/reconciliation problem.

## Epistemic status

`OBSERVED / BOUNDED EXPERIMENT`.

## Limitations

The fixture is deterministic and local. It does not model real distributed authority stores, clock skew, network partitions, multiple human approvers, emergency override, physical effects, or real-world legal authority.

## Public boundary

No Genesis source, private architecture, credentials, internal endpoints, datasets or canonical decisions are included. Interpretation remains in private `genesis-lab`.
