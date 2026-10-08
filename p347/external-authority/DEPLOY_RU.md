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

## Deployment — reproducible temporary authority

Keep one terminal session open while running these blocks so the local variables remain available. The authority source checkout must be exact. For the current bounded baseline, use the v9 source SHA that passed the seven-case discriminator.

~~~bash
set -euo pipefail
REPO_DIR="$HOME/ci-probe-p347-authority"
if [ ! -d "$REPO_DIR/.git" ]; then
  git clone https://github.com/nz-genesis/ci-probe.git "$REPO_DIR"
fi
git -C "$REPO_DIR" fetch origin
test -z "$(git -C "$REPO_DIR" status --porcelain)" || {
  echo "STOP: repository has local changes; preserve them and use a clean checkout."
  exit 1
}
git -C "$REPO_DIR" checkout --detach e63c138ffe833f028a6942c82704c2303d1313c1
SOURCE_SHA="$(git -C "$REPO_DIR" rev-parse HEAD)"
test "$SOURCE_SHA" = "e63c138ffe833f028a6942c82704c2303d1313c1"
printf 'SOURCE_SHA=%s\n' "$SOURCE_SHA"
~~~

Create private secret storage outside the repository. This generates random tokens locally; the values are not printed and the files are not placed in Git.

~~~bash
umask 077
SECRET_DIR="$HOME/.local/share/p347-authority"
mkdir -p "$SECRET_DIR"
chmod 700 "$SECRET_DIR"
python3 - "$SECRET_DIR" <<'PY'
import json, secrets, sys
from pathlib import Path

root = Path(sys.argv[1])
admin = secrets.token_urlsafe(32)
effect = secrets.token_urlsafe(32)
(root / "secrets.json").write_text(json.dumps({
    "P347_ADMIN_TOKEN": admin,
    "P347_EFFECT_TOKEN": effect
}), encoding="utf-8")
(root / "admin-token").write_text(admin, encoding="utf-8")
(root / "effect-token").write_text(effect, encoding="utf-8")
for name in ("secrets.json", "admin-token", "effect-token"):
    (root / name).chmod(0o600)
PY
~~~

Deploy from the exact source checkout. Do not use an unpinned `npx wrangler` command.

~~~bash
set -euo pipefail
SECRET_DIR="$HOME/.local/share/p347-authority"
test -f "$SECRET_DIR/secrets.json" || {
  echo "STOP: rerun the private secret-generation block before deploying a fresh temporary authority."
  exit 1
}
npx --yes wrangler@4.149.0 --version
cd "$REPO_DIR/p347/external-authority"
npx --yes wrangler@4.149.0 deploy --dry-run --strict
npx --yes wrangler@4.149.0 deploy --temporary --strict \
  --secrets-file "$SECRET_DIR/secrets.json" \
  --var "P347_SOURCE_VERSION:$SOURCE_SHA" \
  > "$SECRET_DIR/deployment.raw.txt" 2>&1
~~~

`deployment.raw.txt` contains a temporary-account claim URL and must stay inside the private directory; never commit or share it. Extract the Worker URL locally:

~~~bash
python3 - "$SECRET_DIR/deployment.raw.txt" "$SECRET_DIR/authority-url" <<'PY'
import re, sys
from pathlib import Path

raw = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace")
matches = re.findall(r"https://[A-Za-z0-9.-]+\.workers\.dev", raw)
if not matches:
    raise SystemExit("No workers.dev URL found; inspect the private raw deployment log")
output = Path(sys.argv[2])
output.write_text(matches[-1] + "\n", encoding="utf-8")
output.chmod(0o600)
PY
P347_EXTERNAL_AUTHORITY_URL="$(cat "$SECRET_DIR/authority-url")"
printf 'P347_EXTERNAL_AUTHORITY_URL=%s\n' "$P347_EXTERNAL_AUTHORITY_URL"
~~~

Verify read-only readiness and exact source provenance. This must not mutate authority state.

~~~bash
set -euo pipefail
curl --fail-with-body --connect-timeout 10 --max-time 20 -sS \
  "$P347_EXTERNAL_AUTHORITY_URL/v1/state" \
  | tee "$SECRET_DIR/state-before.json"
python3 - "$SECRET_DIR/state-before.json" <<'PY'
import json, sys
from pathlib import Path

state = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
expected = "e63c138ffe833f028a6942c82704c2303d1313c1"
assert state.get("source_version") == expected, state
assert state.get("generation") == 1, state
assert state.get("effect_count") == 0, state
print("P347_READINESS_AND_SOURCE_PROVENANCE=PASS")
PY
rm -f "$SECRET_DIR/secrets.json"
~~~

Retain `admin-token` and `effect-token` with mode `0600` for the planned physical experiment. Never paste their contents into a command, chat, Git, or evidence log.

**Do not call `/v1/admin/mutate` or `/v1/effects` during deployment smoke checks.** The physical test needs a fresh baseline with generation 1 and effect count 0. Mutation/effect calls are allowed only after the N100 capture and Mac application trace are running and the experiment reaches its planned step.

The temporary account is time-limited (claim window 60 minutes). Coordinate the N100 visibility preflight within that window. Do not reuse a URL from an expired historical artifact. Keep the deployment URL, source SHA, Worker version ID, readiness response and timestamps in private experiment evidence; redact the claim URL and credentials from any shareable copy.

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
