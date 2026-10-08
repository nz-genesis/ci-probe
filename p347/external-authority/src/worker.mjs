import { DurableObject } from "cloudflare:workers";
import { canonicalState, classifyEffect } from "./authority_logic.mjs";

const JSON_HEADERS = { "content-type": "application/json; charset=utf-8" };

function json(body, status = 200) {
  return new Response(JSON.stringify(body), { status, headers: JSON_HEADERS });
}

function textBody(request) {
  return request.text().then(raw => {
    if (!raw) return {};
    const value = JSON.parse(raw);
    if (!value || typeof value !== "object" || Array.isArray(value)) {
      throw new Error("request body must be an object");
    }
    return value;
  });
}

async function sha256Hex(value) {
  const bytes = new TextEncoder().encode(value);
  const digest = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(digest)].map(b => b.toString(16).padStart(2, "0")).join("");
}

export class P347Authority extends DurableObject {
  constructor(ctx, env) {
    super(ctx, env);
    this.ctx.storage.sql.exec(
      `CREATE TABLE IF NOT EXISTS meta (
         key TEXT PRIMARY KEY,
         value TEXT NOT NULL
       );
       CREATE TABLE IF NOT EXISTS effects (
         effect_id TEXT PRIMARY KEY,
         fingerprint TEXT NOT NULL,
         generation INTEGER NOT NULL,
         effect_digest TEXT NOT NULL,
         payload_json TEXT NOT NULL,
         created_at TEXT NOT NULL
       );
       INSERT OR IGNORE INTO meta(key, value) VALUES ('generation', '1');`
    );
  }

  currentGeneration() {
    return Number(this.ctx.storage.sql
      .exec("SELECT value FROM meta WHERE key = 'generation'")
      .one().value);
  }

  effectCount() {
    return Number(this.ctx.storage.sql
      .exec("SELECT COUNT(*) AS count FROM effects")
      .one().count);
  }

  async currentState() {
    const generation = this.currentGeneration();
    const effectCount = this.effectCount();
    const digest = await sha256Hex(JSON.stringify({ generation }));
    return { generation, effect_count: effectCount, state_digest: digest };
  }

  mutate() {
    const next = this.currentGeneration() + 1;
    this.ctx.storage.sql.exec("UPDATE meta SET value = ? WHERE key = 'generation'", String(next));
    return next;
  }

  effect(body, headers) {
    const currentGeneration = this.currentGeneration();
    const effectId = headers.get("Idempotency-Key") || body.effect_id;
    const fingerprint = headers.get("X-Request-Fingerprint");
    const requestedGeneration = body.generation;
    if (!fingerprint) return { status: 400, body: { error: "missing_request_fingerprint" } };

    const existing = effectId
      ? this.ctx.storage.sql.exec(
          "SELECT effect_id, fingerprint, generation, effect_digest FROM effects WHERE effect_id = ?",
          effectId
        ).one()
      : null;

    const decision = classifyEffect({
      currentGeneration,
      requestedGeneration,
      existing,
      effectId,
      fingerprint,
    });

    if (decision.status === 201) {
      const effectDigest = fingerprint;
      this.ctx.storage.sql.exec(
        "INSERT INTO effects(effect_id, fingerprint, generation, effect_digest, payload_json, created_at) VALUES (?, ?, ?, ?, ?, ?)",
        effectId,
        fingerprint,
        requestedGeneration,
        effectDigest,
        JSON.stringify(body.payload ?? null),
        new Date().toISOString()
      );
      return {
        status: 201,
        body: {
          outcome: "OBSERVED_SUCCESS",
          duplicate: false,
          effect_id: effectId,
          generation: requestedGeneration,
          effect_digest: effectDigest,
        },
      };
    }

    return decision;
  }

  async observedEffect(effectId) {
    const row = this.ctx.storage.sql
      .exec("SELECT effect_id, fingerprint, generation, effect_digest, payload_json, created_at FROM effects WHERE effect_id = ?", effectId)
      .one();
    if (!row) return null;
    return {
      effect_id: row.effect_id,
      generation: Number(row.generation),
      fingerprint: row.fingerprint,
      effect_digest: row.effect_digest,
      payload: JSON.parse(row.payload_json),
      created_at: row.created_at,
      outcome: "OBSERVED_SUCCESS",
    };
  }

  async fetch(request) {
    const url = new URL(request.url);
    if (request.method === "GET" && url.pathname === "/v1/state") {
      return json({
        authority: "P347_EXTERNAL_AUTHORITY",
        source_version: this.env.P347_SOURCE_VERSION ?? "unversioned",
        ...(await this.currentState()),
      });
    }

    if (request.method === "POST" && url.pathname === "/v1/admin/mutate") {
      const token = request.headers.get("Authorization");
      if (!this.env.P347_ADMIN_TOKEN || token !== `Bearer ${this.env.P347_ADMIN_TOKEN}`) {
        return json({ error: "forbidden" }, 403);
      }
      const generation = this.mutate();
      return json({
        authority: "P347_EXTERNAL_AUTHORITY",
        source_version: this.env.P347_SOURCE_VERSION ?? "unversioned",
        generation,
      });
    }

    if (request.method === "POST" && url.pathname === "/v1/effects") {
      try {
        const body = await textBody(request);
        const result = await this.effect(body, request.headers);
        return json(result.body, result.status);
      } catch (error) {
        return json({ error: "invalid_request", detail: String(error?.message ?? error) }, 400);
      }
    }

    if (request.method === "GET" && url.pathname.startsWith("/v1/effects/")) {
      const effectId = decodeURIComponent(url.pathname.slice("/v1/effects/".length));
      const result = await this.observedEffect(effectId);
      return result ? json(result) : json({ error: "not_found" }, 404);
    }

    return json({ error: "not_found" }, 404);
  }
}

export default {
  async fetch(request, env) {
    const id = env.P347_AUTHORITY.idFromName("singleton");
    return env.P347_AUTHORITY.get(id).fetch(request);
  },
};
