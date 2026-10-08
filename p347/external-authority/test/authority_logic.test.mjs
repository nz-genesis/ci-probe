import test from "node:test";
import assert from "node:assert/strict";
import { canonicalState, classifyEffect } from "../src/authority_logic.mjs";

test("stale generation is rejected", () => {
  const result = classifyEffect({
    currentGeneration: 2,
    requestedGeneration: 1,
    existing: null,
    effectId: "e1",
    fingerprint: "f1",
  });
  assert.equal(result.status, 409);
  assert.equal(result.body.reason, "STALE_REJECT");
});

test("same key and fingerprint is idempotent", () => {
  const result = classifyEffect({
    currentGeneration: 2,
    requestedGeneration: 2,
    existing: {
      effect_id: "e1",
      fingerprint: "f1",
      generation: 2,
      effect_digest: "d1",
    },
    effectId: "e1",
    fingerprint: "f1",
  });
  assert.equal(result.status, 200);
  assert.equal(result.body.duplicate, true);
});

test("same key with different fingerprint is conflict", () => {
  const result = classifyEffect({
    currentGeneration: 2,
    requestedGeneration: 2,
    existing: {
      effect_id: "e1",
      fingerprint: "f1",
      generation: 2,
      effect_digest: "d1",
    },
    effectId: "e1",
    fingerprint: "f2",
  });
  assert.equal(result.status, 409);
  assert.equal(result.body.reason, "CONFLICT");
});

test("new effect is admitted only at current generation", () => {
  const result = classifyEffect({
    currentGeneration: 2,
    requestedGeneration: 2,
    existing: null,
    effectId: "e2",
    fingerprint: "f2",
  });
  assert.equal(result.status, 201);
  assert.equal(result.body.duplicate, false);
});

test("state digest input is deterministic", () => {
  assert.equal(canonicalState(2, 3), '{"generation":2,"effect_count":3}');
});
