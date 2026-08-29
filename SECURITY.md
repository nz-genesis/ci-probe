# Security and Confidentiality Boundary

## Scope

`nz-genesis/ci-probe` is a public, Genesis-agnostic execution-control repository.

## Never publish here

Do not commit, paste, upload, or otherwise expose:

- Genesis source code or private implementation;
- Genesis architecture, ontology, primitives, or unpublished design;
- private research corpus, fixtures, prompts, cases, or datasets;
- unpublished hypotheses, conclusions, negative results, or decision records;
- private CI configuration or internal operational details;
- credentials, access tokens, API keys, cookies, certificates, or secrets;
- private evidence, logs, artifacts, or screenshots from `nz-genesis/genesis-lab`;
- links or references that disclose confidential repository contents beyond what is necessary for public provenance.

## What belongs here

Only generic CI substrate diagnostics and deliberately public reproducibility material may be committed.

The default probe must remain independent of Genesis and must not require Genesis secrets or private repository access.

## Result flow

Results generated here are **external evidence**. They do not automatically enter or modify `nz-genesis/genesis-lab`.

The controlled flow is:

`public run → raw execution evidence → provenance → validation/review → explicit acceptance → Genesis Lab`

Any transfer to `genesis-lab` must be deliberate, scoped, provenance-preserving, and performed through the applicable Genesis research protocol.

## Incident rule

If confidential Genesis material is accidentally committed here, stop further publication immediately. Do not attempt to conceal or rewrite the event as if it never happened; preserve the incident provenance and remediate according to the applicable security procedure.
