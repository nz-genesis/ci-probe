# P209 Public Red Team

The public verifier must reject:

- missing required identity fields;
- extra/private fields;
- state/execution/witness digest substitution;
- predicate substitution;
- projection-version substitution;
- stale or replayed envelope metadata;
- any claim that public validation proves private Genesis semantics.

This is contract-level verification only. It cannot establish private semantic truth.

Status: `OPEN — WAITING FOR REAL PRIVATE DERIVED ENVELOPE`.
