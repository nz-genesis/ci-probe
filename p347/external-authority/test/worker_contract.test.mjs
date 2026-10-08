import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const source = fs.readFileSync(new URL("../src/worker.mjs", import.meta.url), "utf8");

function methodBody(name) {
  const marker = `  ${name}(`;
  const start = source.indexOf(marker);
  assert.notEqual(start, -1, `missing method ${name}`);
  const next = source.indexOf("\n  }", start);
  assert.notEqual(next, -1, `unterminated method ${name}`);
  return source.slice(start, next);
}

test("effect admission path has no async interleaving gap", () => {
  const body = methodBody("effect");
  assert.equal(body.includes("await "), false);
  assert.ok(body.indexOf("classifyEffect") < body.indexOf("INSERT INTO effects"));
});

test("generation mutation path has no async interleaving gap", () => {
  const body = methodBody("mutate");
  assert.equal(body.includes("await "), false);
  assert.ok(body.includes("UPDATE meta SET value"));
});


test("effect lookup tolerates absent idempotency record", () => {
  const body = methodBody("effect");
  assert.match(body, /SELECT effect_id, fingerprint, generation, effect_digest FROM effects WHERE effect_id = \?/);
  assert.match(body, /toArray\(\)\[0\] \?\? null/);
  assert.doesNotMatch(body, /SELECT effect_id, fingerprint, generation, effect_digest FROM effects WHERE effect_id = \?[\s\S]*?\.one\(\)/);
});
