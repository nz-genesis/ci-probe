# Durable Operation Ledger Recovery — 2026-08-31

## Question
Can a durable operation record preserve enough local lineage across process restart to distinguish prepared, attempted, and confirmed states without treating the ledger as proof of an external-world effect?

## Discriminator
This is distinct from the prior timeout impossibility pass: the new variable is durable operation/effect identity across restart, with explicit reconciliation against an independent observation.

## Result
`DURABLE OPERATION LEDGER RECOVERY: 6/6 PASS` in the committed clean-room executable.

## Findings
- PREPARED survives restart as `READY_TO_EXECUTE`.
- EFFECT_ATTEMPTED without observation remains `UNKNOWN`.
- Matching independent effect identity closes the operation as `CONFIRMED`.
- A mismatching observation does not close the operation.
- CONFIRMED state is reconstructible after restart when the effect identity is retained.
- Operation identity alone is not world-state evidence.

## Red Team
The negative controls specifically prevent local operation state or a mismatching observation from being promoted to external truth.

## Primitive reduction
No new Genesis primitive is justified. A durable operation ledger is an implementation/representation of State + Lineage + Execution semantics, not a new irreducible primitive.

## Status
`BOUNDED / LOCAL VERIFIED / HOSTED-CI PENDING / NOT CANONICAL`

## Next discriminator
Evaluate crash/restart with concurrent operations and reconciliation races, only if this adds a new semantic failure boundary beyond existing concurrency and atomicity research.
