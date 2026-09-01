# Pass 49 Hosted Execution Evidence

This document records the public execution substrate used to obtain independently fetchable GitHub Actions evidence for Pass 49.

## Boundary

- Private semantic/research state remains in `nz-genesis/genesis-lab`.
- Public execution/control substrate is `nz-genesis/ci-probe`.
- No private semantic state, authority payload, or private witness material belongs in this repository.

## Required evidence chain

```text
checkout github.sha
→ verify git rev-parse HEAD == GITHUB_SHA
→ execute Pass 49 public-safe probe
→ capture stdout
→ upload exact-SHA evidence artifact
→ fetch run
→ fetch jobs/steps
→ fetch logs
→ fetch artifact
→ verify artifact contents against exact SHA
```

CI success alone is not semantic proof. The hosted run is only execution evidence for the public-safe probe and must be reconciled with the private research record in `genesis-lab`.

## Pass 49 semantic boundary

The probe tests crash-after-external-effect reconciliation without introducing a new Genesis primitive. The current candidate basis remains:

`State + Transition + Capability + Authority + Observation + Evidence + Constraint`

The public probe must not imply that capability is authority, observation is execution proof, UNKNOWN is success/retry permission, or a missing local record proves absence of an external effect.

## Verification status

Hosted evidence is considered verified only after the exact run, jobs/steps, logs, and artifact are fetched and the artifact checkout identity matches the triggering SHA.

Verified reference run: `33523176539`; exact triggering SHA: `bc4db6de927eb02b84e77c03fde012489acf0ec5`; artifact: `9806581071`.
