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

  // Resolve an already-recorded idempotency key before checking freshness.
  // After a committed effect loses its ACK, the authority may advance before
  // the retry arrives. The retry must recover the recorded outcome, not hide
  // it behind STALE_REJECT and tempt the caller to create a new effect.
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

  if (requestedGeneration !== currentGeneration) {
    return {
      status: 409,
      body: {
        reason: requestedGeneration < currentGeneration ? "STALE_REJECT" : "CONFLICT",
        generation: currentGeneration,
      },
    };
  }

  return { status: 201, body: { outcome: "OBSERVED_SUCCESS", duplicate: false, effect_id: effectId } };
}
