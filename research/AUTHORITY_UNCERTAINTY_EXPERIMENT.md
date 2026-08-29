# Authority uncertainty experiment

## Question

Can uncertainty about current authority be represented as a derived classification over evidence, without creating `UnknownAuthority` or `ConflictingAuthority` primitives?

## Evidence-derived states

Given two independent evidence dimensions — valid-authority evidence and revocation evidence — derive:

- `AUTHORIZED` = valid evidence only;
- `REVOKED` = revocation evidence only;
- `UNKNOWN` = neither evidence;
- `CONFLICTING` = both evidence.

These are classifications, not primitives.

## Admission mechanisms

- `optimistic` — admits UNKNOWN (deliberate unsafe counterexample);
- `fail-closed` — admits only AUTHORIZED.

## Observed result

The fail-closed strategy preserves the boundary for UNKNOWN, REVOKED, and CONFLICTING. The optimistic strategy demonstrates the semantic risk of treating missing evidence as authorization.

This supports the distinction:

```text
unknown authority
≠
revoked authority
≠
authorized authority
≠
conflicting authority
```

The result does not require a new primitive for each state. The states can be derived from evidence and constraints.

## Epistemic boundary

This is not a theorem that fail-closed is always the correct policy. It demonstrates only that the policy decision must not erase the epistemic distinction between known authorization and uncertainty/conflict when an irreversible boundary is present.

## Limitations

No real distributed evidence propagation, clock uncertainty, trust hierarchy, Byzantine evidence, physical effect, or legal authority is modeled.

## Public boundary

No Genesis-specific private architecture, credentials, datasets, internal endpoints or canonical decisions are included. Interpretation remains in private `genesis-lab`.
