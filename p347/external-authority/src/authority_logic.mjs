export function canonicalState(generation, effectCount) {
  return JSON.stringify({ generation, effect_count: effectCount });
}

export function classifyEffect({ currentGeneration, requestedGeneration, existing, effectId, fingerprint }) {
  if (!Number.isInteger(requestedGeneration) || requestedGeneration < 0) {
    return { status: 400, body: { error: "invalid_generation" } };
  }
  if (!effectId || !fingerprint) {
    return { status: 400, body: { error: "missing_idempotency_contract" } };
  }
  if (requestedGeneration !== currentGeneration) {
    return {
      status: 409,
      body: {
        reason: requestedGeneration < currentGeneration ? "STALE_REJECT" : "CONFLICT",
        generation: currentGeneration,
      },
    };
  }
  if (existing) {
    if (existing.fingerprint !== fingerprint) {
      return { status: 409, body: { reason: "CONFLICT", effect_id: effectId } };
    }
    return {
      status: 200,
      body: {
        outcome: "OBSERVED_SUCCESS",
        duplicate: true,
        effect_id: effectId,
        generation: existing.generation,
        effect_digest: existing.effect_digest,
      },
    };
  }
  return { status: 201, body: { outcome: "OBSERVED_SUCCESS", duplicate: false, effect_id: effectId } };
}
