# BIR-1A Review Checklist

Status: `REVIEW PROTOCOL — NOT EVIDENCE`

Use only after a blind result has been frozen. Do not expose Genesis interpretation to the reviewer before this checklist is completed.

## A. Challenge integrity

- [ ] Challenge ID matches the frozen experiment.
- [ ] Challenge SHA-256 matches the frozen artifact.
- [ ] No post-run challenge modification occurred.

## B. Context isolation

- [ ] Participant received only the permitted challenge and role contract.
- [ ] No Genesis private corpus was supplied.
- [ ] No previous Genesis adjudication was supplied.
- [ ] No expected ontology or target answer was supplied.
- [ ] Delivery logs contain no prohibited material.

## C. Execution provenance

- [ ] Model/provider identity is recorded at the declared granularity.
- [ ] Runtime/version is recorded.
- [ ] Solver artifact digest is recorded.
- [ ] Configuration digest is recorded.
- [ ] Prompt-contract digest is recorded.
- [ ] Execution timestamps are recorded.
- [ ] Raw-result SHA-256 matches the frozen raw artifact.
- [ ] Commitment/reveal verifies.

## D. Actor independence

- [ ] Participant/operator relationship is explicitly declared.
- [ ] Prior Genesis exposure is explicitly declared.
- [ ] External control of the runtime is corroborated where claimed.
- [ ] Reviewer has checked for hidden Genesis operator control.
- [ ] `unknown` is preserved where evidence is insufficient.

## E. Adversarial result review

- [ ] Search for hidden assumptions.
- [ ] Search for omitted state distinctions.
- [ ] Search for conflation of local truth with external effect.
- [ ] Test retry/ack-loss/crash counterexamples where applicable.
- [ ] Test exactly-once versus at-least-once claims where applicable.
- [ ] Attack minimality: identify any primitive that can be removed without loss.
- [ ] Attack completeness: identify scenarios not represented by the proposed model.
- [ ] Record strongest disconfirming argument before comparison with Genesis.

## F. Epistemic classification

The reviewer MUST classify each claim as one of:

- `OBSERVED` — directly supported by the frozen artifacts;
- `DERIVED` — follows from stated assumptions and observed artifacts;
- `HYPOTHESIS` — plausible but unverified;
- `UNKNOWN` — evidence insufficient;
- `CONTRADICTED` — conflicts with frozen evidence.

Agreement with Genesis is not a review criterion.

## Final gate

The reviewer may recommend `READY_FOR_GENESIS_ADJUDICATION` only when the raw result is frozen, the adversarial review is frozen, and no unresolved provenance or contamination issue is being silently treated as proof.
