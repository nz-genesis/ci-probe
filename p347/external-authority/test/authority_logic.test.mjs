import test from "node:test";
import assert from "node:assert/strict";
import { canonicalState, classifyEffect } from "../src/authority_logic.mjs";

const existingEffect = {
  effect_id: "e1",
  fingerprint: "f1",
  generation: 2,
  effect_digest: "d1",
};

test("stale generation is rejected for a new effect", () => {
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
    existing: existingEffect,
    effectId: "e1",
    fingerprint: "f1",
  });
  assert.equal(result.status, 200);
  assert.equal(result.body.duplicate, true);
  assert.equal(result.body.effect_id, "e1");
});

test("same key and fingerprint recovers committed effect after authority advances", () => {
  const result = classifyEffect({
    currentGeneration: 3,
    requestedGeneration: 2,
    existing: existingEffect,
    effectId: "e1",
    fingerprint: "f1",
  });
  assert.equal(result.status, 200);
  assert.equal(result.body.duplicate, true);
  assert.equal(result.body.generation, 2);
  assert.equal(result.body.effect_digest, "d1");
});

test("same key with different fingerprint remains conflict after authority advances", () => {
  const result = classifyEffect({
    currentGeneration: 3,
    requestedGeneration: 2,
    existing: existingEffect,
    effectId: "e1",
    fingerprint: "f2",
  });
  assert.equal(result.status, 409);
  assert.equal(result.body.reason, "CONFLICT");
});

test("same key with different fingerprint is conflict", () => {
  const result = classifyEffect({
    currentGeneration: 2,
    requestedGeneration: 2,
    existing: existingEffect,
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

test("future generation without an existing key is a conflict", () => {
  const result = classifyEffect({
    currentGeneration: 2,
    requestedGeneration: 3,
    existing: null,
    effectId: "e3",
    fingerprint: "f3",
  });
  assert.equal(result.status, 409);
  assert.equal(result.body.reason, "CONFLICT");
});

test("negative generation is rejected", () => {
  const result = classifyEffect({
    currentGeneration: 2,
    requestedGeneration: -1,
    existing: null,
    effectId: "e4",
    fingerprint: "f4",
  });
  assert.equal(result.status, 400);
  assert.equal(result.body.error, "invalid_generation");
});

test("state digest input is deterministic", () => {
  assert.equal(canonicalState(2, 3), '{"generation":2,"effect_count":3}');
});


test("canonical state representation changes when effect count changes", () => {
  assert.notEqual(canonicalState(2, 1), canonicalState(2, 2));
});
