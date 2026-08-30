# Durable Crash / External Effect Recovery — 2026-08-31

## Question
Can Genesis safely recover an external effect after a crash that occurs after the provider applies the effect but before local acknowledgement becomes durable?

## Discriminator
This is not a replay or generic coordinator test. The discriminator is the information boundary between local durable state and independently observable external state, with provider idempotency as an explicit contract property.

## Local model
The probe models:
- durable acknowledgement;
- crash after external effect;
- independent observation;
- idempotent retry;
- non-idempotent retry;
- contradictory observation overriding a local acknowledgement.

## Result
`DURABLE CRASH EXTERNAL EFFECT RECOVERY: 6/6 PASS` in the committed executable.

## Findings
1. A durable acknowledgement supports an `ACKNOWLEDGED` state.
2. A crash after effect without observation leaves the world state `UNKNOWN`.
3. Independent observation can resolve the ambiguity to `CONFIRMED`.
4. Provider-side idempotency makes retry safe for the same operation identity.
5. Retrying a non-idempotent provider duplicates the modeled effect.
6. A contradictory independent observation must not be overridden by a local ACK.

## Red Team / negative boundary
The earlier non-idempotent-timeout impossibility result remains valid: if no independent effect observation exists and the provider supplies no idempotency guarantee, local recovery cannot distinguish `effect happened` from `effect did not happen` safely.

## Primitive reduction
No new Genesis primitive is introduced. Provider idempotency is a capability/contract property; observation, evidence, verification, state, execution and authority remain composable responsibilities.

## Status
`BOUNDED / LOCAL VERIFIED / HOSTED-CI PENDING / NOT CANONICAL`

## Next discriminator
Test a durable operation ledger across process crash/restart and distinguish local acknowledgement, provider effect identity, independent observation, and recovery authorization. This must add a new discriminator rather than repeat timeout or replay tests.
