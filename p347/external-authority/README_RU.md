# P347 — внешний authority substrate

## Назначение

Этот каталог содержит **реальный внешний execution substrate**, а не Genesis semantic primitive.

Authority реализован как Cloudflare Worker + SQLite-backed Durable Object. Durable Objects предоставляют уникальный stateful instance и транзакционное/strongly-consistent persistent storage; это актуальный внешний realization mechanism, а не часть Genesis ontology. Cloudflare рекомендует SQLite-backed Durable Objects для новых namespaces. citeturn7search0turn7search2

## Контракт

Endpoints:

- `GET /v1/state` — authoritative generation + state digest;
- `POST /v1/admin/mutate` — управляемая смена generation; требует `Authorization: Bearer ...`;
- `POST /v1/effects` — consequential state change с обязательными `Authorization`, `Idempotency-Key` и `X-Request-Fingerprint`;
- `GET /v1/effects/<effect_id>` — fresh re-observation.

Semantics:

- stale generation → `409 STALE_REJECT`;
- same idempotency key + same fingerprint → duplicate retry, без второго effect;
- same idempotency key + different fingerprint → `409 CONFLICT`;
- current generation + new key → new observed effect;
- effect state is persisted before the response is returned by the Durable Object storage/output-gate model.

## Deployment

For a one-off experiment, current Cloudflare supports unauthenticated `wrangler deploy --temporary`, which provisions a temporary account and returns a claim URL. Temporary resources are deleted if the account is not claimed within the stated window. For a persistent authority, use a permanent Cloudflare account and scoped credentials. citeturn2search0turn2search3

Do not put `P347_ADMIN_TOKEN` in Git.

## Evidence boundary

A green unit test does not establish external authority. The admissible authority evidence must include:

1. deployed external URL;
2. exact deployed source/version provenance;
3. independently observed state;
4. successful mutation;
5. effect admission/rejection traces;
6. fresh re-observation;
7. external network witness;
8. raw traces preserved outside the candidate's process.

This substrate intentionally does not claim any of those until the deployment is actually executed.
