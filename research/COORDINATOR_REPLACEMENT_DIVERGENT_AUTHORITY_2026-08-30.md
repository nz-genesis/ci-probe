# Coordinator Replacement With Divergent Authority — 2026-08-30

## Status
BOUNDED / LOCAL MODEL PASS / HOSTED CI PENDING

## Bounded question
Can coordinator replacement with divergent authority histories be resolved using only local operation identity, version, and uniqueness state?

## Material novelty
This is not a replay, stale-negative, coordinator-loss, or ordinary network-partition test. The discriminator is divergent coordinator authority: replacement coordinator B lacks the durable history proving coordinator A's prior commit, while both retain the same operation identity and version.

## Local result
`DIVERGENT COORDINATORS: LOCAL STATE CANNOT RESOLVE AUTHORITY EQUIVOCATION`
`12/12 PASS`

## Result
Both divergent coordinators can locally regard the same operation as admissible because their local state contains the same operation identity and version but different authority histories. Without a shared authoritative history or fencing fact, local uniqueness and version constraints cannot select a single winner across divergent coordinators.

## Red Team
1. This is a constructed counterexample to extending single-domain uniqueness across divergent authorities.
2. The result does not establish that a specific consensus protocol is required.
3. The result does establish that some authoritative ordering/fencing/canonical history is an additional requirement for this topology.
4. The probe does not claim Byzantine consensus, production storage safety, or physical-world exactly-once execution.

## Primitive reduction
No new Genesis primitive is demonstrated. The counterexample is an architecture/evidence boundary: authority history and fencing cannot be inferred from local operation identity/version alone. Whether this belongs in Genesis semantics or remains an implementation/governance mechanism is unresolved and must be tested against the private Genesis correspondence before any ontology change.

## Evidence boundary
Executable public artifact and workflow are present. Hosted completion must be independently inspected before claiming public-CI verification.

## Omission gate
Open: real coordinator replacement and fencing semantics, trust-root equivocation, cross-domain consumption, dynamic delegation races, multi-step irreversible transactions, private Genesis-to-public semantic correspondence, external physical-world verification, privacy under adaptive observation, and global minimality.

## Decision
Do not add a Genesis primitive from this experiment alone. Do not open P190. Treat authority-history/fencing as a newly demonstrated external-realization boundary and test whether the distinction is already represented by Genesis authority/temporal/evidence semantics before considering architectural change.
