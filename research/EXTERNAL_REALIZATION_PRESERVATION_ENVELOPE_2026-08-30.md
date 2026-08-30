# External Realization Preservation Envelope — 2026-08-30

## Status
BOUNDED RESEARCH / GENERIC CLEAN-ROOM / NOT GENESIS CANONICAL

## Question
Can a generic external realization boundary carry the material dimensions needed to distinguish authority, resource version, temporal admissibility, and verification without exposing private Genesis semantics, and can omission of each tested dimension be detected?

## Genealogy
The preceding `external_realization_boundary.py` intentionally projected only a small public allow-list. Its mutation Red Team showed that changes to authority, resource version, temporal constraint, and verification remained observationally identical after projection. That projection is therefore rejected as a sufficient semantic contract.

This experiment is a correction, not a repetition: it tests an explicit generic preservation envelope plus ablation and mutation attacks.

## Envelope
The envelope contains only generic identifiers, numeric codes/bounds, an observed epoch, an expected numeric value, and an irreversibility flag. No Genesis-specific ontology labels, private data, credentials, or internal architecture are used.

## Tests
1. Mutation test: each tested material dimension changes the envelope digest; authority/version/time/verification mutations also change the derived admissibility/verification outcome.
2. Ablation test: removing the tested material dimension makes the corresponding paired inputs collide at that projection level.
3. Mechanism independence remains a future requirement; this artifact does not claim independent private/public correspondence.

## Interpretation
The experiment supports a generic statement: a public realization contract cannot omit a dimension that materially changes the bounded decision while still claiming semantic preservation for that decision.

It does NOT prove that this is the minimal Genesis boundary, does NOT prove a finite universal basis, and does NOT justify Action/Execution/Recovery/HITL as Genesis primitives.

## Red Team
- Value-level leakage: generic numeric/code representation only; no domain-specific semantic labels.
- Laundering: envelope fields are tested by mutation and ablation rather than accepted by name.
- Overclaim: no private Genesis correspondence is inferred.
- Replay/substitution: digest is carried as evidence, but cryptographic provenance binding to a private contract remains untested.
- Irreversibility: included as a tested dimension, but no claim is made that it is always necessary.

## Omission gate
`Ничего ли мы не упустили?`

Material remaining gaps are private-side correspondence, provenance binding, replay/non-substitution, independent realization mechanisms for this corrected envelope, and external-world realization beyond the generic deterministic fixture. These are not silently closed by this experiment.

## Decision
Keep external realization `UNRESOLVED / EXPERIMENTAL`. The earlier simple projection remains rejected. Do not promote this envelope to canonical Genesis architecture.
