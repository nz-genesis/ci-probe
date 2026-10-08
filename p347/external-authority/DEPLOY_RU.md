# P347 external authority — deployment contract

## Current verified toolchain — 2026-10-09

For this bounded P347 experiment, Wrangler `4.149.0` is the verified release baseline. The official release was published at `2026-10-08T18:33:04Z`, and v9 run `37847810217` executed on that version with readiness PASS and seven semantic cases PASS. Release record: https://github.com/cloudflare/workers-sdk/releases/tag/wrangler%404.149.0

Do not treat `4.148.0` as current for this research pass: it was used by later v10-v12 runs after `4.149.0` had already been published. Those failures remain run-specific negative genealogy; they do not invalidate the v9 receipt or prove a universal version defect.

Because `wrangler deploy --temporary` creates a time-limited external account (the claim window is 60 minutes), a physical N100 witness run must use a freshly deployed live authority and be coordinated within its live window. Do not reuse the URL from an expired historical artifact. The current-tool semantic discriminator need not be repeated merely to refresh the URL; record exact source/version, readiness and the new deployment identity.


## Цель

Развернуть authority **вне GitHub** с exact source provenance и без помещения admin credential в repository.

Для одноразового bounded experiment допустим актуальный Cloudflare temporary deployment. Cloudflare документирует wrangler deploy --temporary как способ создать временный preview account без предварительной аутентификации; deployment и claim URL имеют ограниченный срок. Для постоянного authority следует использовать собственный Cloudflare account и scoped token. См. актуальную документацию Cloudflare: https://developers.cloudflare.com/workers/platform/claim-deployments/

## Требования

- Wrangler `4.149.0` for the current verified experiment; re-run the Freshness Gate before changing the pin.
- Cloudflare Worker + SQLite-backed Durable Object;
- P347_ADMIN_TOKEN и P347_EFFECT_TOKEN хранятся только как Worker secrets;
- source version передаётся через --var P347_SOURCE_VERSION:<exact-commit>;
- deployment URL фиксируется в experiment evidence;
- после deployment сначала выполняются только smoke/contract checks;
- semantic P347 effect run начинается только после независимой проверки state/mutation/re-observation.

## Deployment

Из корня репозитория:

~~~
cd p347/external-authority
npx wrangler --version
npx wrangler deploy --temporary --var "P347_SOURCE_VERSION:$(git rev-parse HEAD)"
~~~

Если Wrangler уже аутентифицирован в постоянном Cloudflare account, --temporary применять нельзя; используйте обычный wrangler deploy с scoped credentials.

После deployment сохранить отдельно:

- Worker URL;
- deployment/version identifier;
- exact source commit;
- observed GET /v1/state result.

Admin token создаётся отдельно и **никогда не записывается в Git**. Его следует передать как Worker secret:

~~~
npx wrangler secret put P347_ADMIN_TOKEN
npx wrangler secret put P347_EFFECT_TOKEN
~~~

После этого проверить mutation через HTTPS. Не помещать Bearer token в shell history или evidence:

~~~
curl --fail-with-body -sS -X POST   -H "Authorization: Bearer $P347_ADMIN_TOKEN"   "$P347_EXTERNAL_AUTHORITY_URL/v1/admin/mutate"
~~~

Секрет не должен попадать в command history, workflow logs или evidence artifact.

## Evidence boundary

Успешный deployment не является P347 semantic evidence.

Admissible external-authority evidence требует отдельного raw record:

- external authority identity;
- deployment/source version;
- state before mutation;
- state after mutation;
- worker qualification generation;
- effect request;
- effect outcome;
- fresh effect re-observation;
- independent packet witness;
- raw packet capture/provenance.

## Current external baseline

Cloudflare Durable Objects сейчас используют strongly-consistent transactional storage и рекомендуют SQLite backend для новых namespaces. Это сильный realization substrate для authority state, но не Genesis semantic primitive. См. https://developers.cloudflare.com/durable-objects/best-practices/access-durable-objects/ и https://developers.cloudflare.com/durable-objects/reference/durable-objects-migrations/

AWS S3 conditional-write semantics используются только как comparative external baseline: If-Match защищает conditional write от устаревшего ETag, а concurrent writes могут возвращать conflict. Это подтверждает, что stale-write fencing/idempotency имеют зрелые реализационные аналоги, но не доказывает Genesis ontology. См. https://docs.aws.amazon.com/AmazonS3/latest/userguide/conditional-writes.html
