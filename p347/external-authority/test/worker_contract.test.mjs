import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";

const source = fs.readFileSync(new URL("../src/worker.mjs", import.meta.url), "utf8");

function methodBody(name) {
  const marker = new RegExp(`  (?:async )?${name}\\(`);
  const match = marker.exec(source);
  assert.notEqual(match, null, `missing method ${name}`);
  const start = match.index;
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


test("state digest includes generation and effect count", () => {
  const body = methodBody("currentState");
  assert.match(body, /canonicalState\(generation, effectCount\)/);
  assert.match(body, /sha256Hex\(state\)/);
});

test("missing effect observation is handled without one-row exception", () => {
  const body = methodBody("observedEffect");
  assert.match(body, /\.toArray\(\)\[0\] \?\? null/);
  assert.doesNotMatch(body, /\.one\(\)/);
});
