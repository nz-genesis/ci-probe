# External Realization Provenance / Replay — 2026-08-30

## Status
BOUNDED RESEARCH / GENERIC CLEAN-ROOM / NOT GENESIS CANONICAL

## Question
Can a generic realization receipt bind a private semantic commitment to one public envelope, one realization identity, one observed effect and one nonce strongly enough to reject bounded replay and substitution attacks without exposing the private semantic contract?

## Prior-art boundary
The preceding preservation-envelope experiment established only mutation/ablation behaviour. Its own omission gate explicitly left provenance binding and replay/non-substitution untested. This experiment therefore changes the discriminator rather than repeating the envelope mutation matrix.

## Model
The private side has a contract commitment. The public envelope carries only the opaque commitment, request identity, nonce and generic operation/version/observation values. A realization receipt binds envelope digest, realizer identity, effect digest and nonce under a verifier-side secret. The verifier also keeps consumed-nonce state.

The fixture is intentionally generic. The verifier key is a test-only clean-room secret and is not evidence that Genesis requires HMAC, a particular cryptographic primitive, or any particular implementation.

## Tests
1. Baseline acceptance succeeds for an untampered receipt.
2. Replaying the same receipt after nonce consumption is rejected.
3. Substituting resource version/envelope data is rejected because the envelope digest no longer matches.
4. Substituting the private contract is rejected because the commitment no longer matches.
5. Substituting the realizer identity is rejected because the receipt tag no longer verifies.
6. Substituting the observed effect is rejected because the receipt tag no longer verifies.

## Red Team
- Digest-only laundering: rejected as insufficient; the receipt binds multiple observations rather than relying on an unbound digest.
- Replay: explicit consumed-nonce state is required; digest equality alone is not replay protection.
- Envelope substitution: rejected by envelope-digest binding.
- Private-contract substitution: rejected by commitment binding.
- Realizer substitution: rejected by realizer identity binding.
- Effect substitution: rejected by effect binding.
- Key disclosure: the test key is a fixture secret; no claim is made about production key management.

## Interpretation
The bounded model demonstrates that provenance/replay/non-substitution can be represented as relations and verification constraints around a generic envelope. It does not establish that HMAC, nonce state, receipts, or any named security mechanism is a Genesis primitive.

It also does not establish real-world key custody, distributed nonce coordination, trust-root authenticity, Byzantine realizers, cryptographic algorithm choice, side-channel resistance, or physical-world effect attribution.

## Omission gate
Still open: distributed replay races across independent verifiers, trust-root equivocation, key rotation/revocation, cross-operation causal coupling, partial external effects, physical-world verification, privacy under adaptive observation, and private-to-public semantic correspondence using a real private Genesis contract.

## Decision
Keep external realization `UNRESOLVED / EXPERIMENTAL`. Do not promote the generic receipt model to Genesis architecture. The next required evidence is private-side correspondence plus a distributed replay/non-substitution attack model, not another single-node envelope mutation experiment.
