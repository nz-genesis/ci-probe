# Shared-Domain Atomic Consumption — 2026-08-30

## Question
Does a single coordinated consumption domain prevent duplicate consumption when two independent verifiers observe the same admissible pre-state and race to commit the same commitment/nonce?

## Why this is new
The prior distributed replay race demonstrated that independent local consumed-state sets are insufficient. This pass changes the discriminator: both verifiers use one shared coordination domain and an explicit commit boundary. It therefore does not repeat local replay testing.

## Clean-room boundary
The fixture uses opaque commitment/nonce identifiers and numeric versions only. It does not encode Genesis ontology, Action, Execution, Recovery, or product architecture.

## Tested interleaving
1. Verifier A and B both observe the same admissible pre-state.
2. A commits first.
3. B commits second.
4. A retries.
5. B retries.
6. A third attempt uses a stale version.

## Result
The bounded model yields exactly one successful commit. The second concurrent commit and all subsequent duplicate retries are rejected. The stale-version attempt is rejected.

## Interpretation
This supports a bounded property of the tested coordination model: one shared consumption state with a commit-time uniqueness check can prevent the duplicate consumption that independent verifier-local state could not prevent.

This does not establish that a particular database, lock, consensus protocol, or AtomicityEngine is a Genesis primitive. It also does not establish distributed correctness under arbitrary partitions, Byzantine actors, unavailable coordinators, or cross-domain authority races.

## Red Team
- Local replay protection was not reused as evidence.
- Both contenders are allowed to prepare successfully, so the result is not caused by preemptive serialization at read time.
- Commit order is adversarially fixed as A then B.
- Duplicate delivery is explicitly retried after the first commit.
- A stale version is tested after the successful commit.

## Omission gate
Still open: crash between prepare and commit, coordinator loss, partitioned domains, concurrent authority change, trust-root equivocation, and cross-resource non-commutative effects.

## Canonical impact
Global Purpose: unchanged.
Genesis ontology: unchanged.
Canonical architecture: unchanged.
New Genesis primitives: 0.
P190: not started.

## Evidence status
Local executable probe: expected 5/5 assertions.
Hosted CI: workflow triggered by the committed artifact; promotion requires inspection of the exact executable step and conclusion, not merely workflow presence.
