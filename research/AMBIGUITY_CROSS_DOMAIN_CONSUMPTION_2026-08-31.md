# P192 — Ambiguity-Preserving Cross-Domain Consumption

Date: 2026-08-31
Status: bounded executable probe; hosted verification pending.

## Question
Does cross-domain consumption preserve unresolved semantic alternatives rather than silently collapsing them, while allowing a downstream action only when it is safe across all unresolved candidates?

## Distinct discriminator
P190 cross-domain consumption tested exact envelope interoperability. P191 tested ambiguity-aware governed action within one decision context. P192 composes the two: the ambiguous candidate set itself crosses a domain boundary and the consumer must not use authority as a truth filter.

## Expected behavior
- unique authorized candidate → `CONSUME`
- multiple candidates, unsafe action → `UNRESOLVED`
- multiple candidates, action safe for all candidates → `SAFE_CONSUME`
- authorized + unauthorized candidates → still `UNRESOLVED`
- unique unauthorized candidate → `UNAUTHORIZED`

## Red Team
1. Highest-authority candidate must not erase a competing interpretation.
2. An unauthorized candidate must not be removed merely because the consumer cannot act on it.
3. Safe-for-all is a stronger condition than merely reversible.
4. Domain transfer must not collapse the candidate set to a single label.

## Reduction
No new primitive is introduced. The behavior is composition of transferred candidate state, authority, action constraints and transition/consumption semantics.

## Limits
This does not prove arbitrary schema evolution, lossy translation, Byzantine transport, cryptographic authenticity, or universal semantic interoperability. Hosted CI is separate evidence from local execution.
