import { describe, expect, it } from "vitest";
import { PROCESS_PROVIDER } from "./src/application/ProcessEvidence.js";
import {
  buildReconstructionObligationLedgerEvidenceValidated,
  resolveReconstructionObligationLedgerRequest,
} from "./src/application/ReconstructionObligationLedgerService.js";
import { EMPTY_PROCESS_CAPTURE_EXAMPLE } from "./src/domain/processCapture.fixture.js";
import { createEvidence, type Evidence } from "./src/domain/evidence.js";
import { createEvidenceBundle } from "./src/domain/evidenceBundle.js";
import { jsonValueSchema } from "./src/domain/jsonValue.js";
import { processCaptureSchema } from "./src/domain/processCapture.js";
import {
  reconstructionObligationLedgerSchema,
  type ReconstructionObligationLedgerInput,
  type ReconstructionObligationLedger,
  type ReviewedReconstructionObligation,
} from "./src/domain/reconstructionObligationLedgerSchemas.js";

const proof = (
  id: string,
  obligationId: string,
  authority: "shipped-artifact" | "controlled-replay" = "controlled-replay",
) =>
  createEvidence(
    undefined,
    { id: `proof-${id}`, name: "Reconstruction proof", version: "1" },
    {
      predicateType: "rea.reconstruction-proof",
      operation: "verify_reconstruction_obligations",
      parameters: {},
      result: {
        passed: true,
        obligation_ids: [obligationId],
        fixture_ids: [
          "fixture.positive",
          "fixture.negative",
          "fixture.cancellation",
          "fixture.teardown",
        ],
        case_kinds: ["positive", "negative", "cancellation", "teardown"],
        verifier_ids: ["verifier.fixture"],
        claim_ids: ["claim.fixture"],
      },
      confidence: "observed",
      authority,
    },
  );

const processEvidence = () =>
  createEvidence(undefined, PROCESS_PROVIDER, {
    predicateType: "rea.process-capture",
    operation: "capture_process_scenario",
    parameters: {},
    result: jsonValueSchema.parse(
      processCaptureSchema.parse(EMPTY_PROCESS_CAPTURE_EXAMPLE),
    ),
    confidence: "observed",
    authority: "controlled-replay",
  });

const request = (
  records: readonly Evidence[],
  overrides: Partial<ReconstructionObligationLedgerInput> = {},
): ReconstructionObligationLedgerInput => ({
  evidence_bundle: createEvidenceBundle(records),
  reviewed_obligations: [],
  manifest: { bindings: [], contradictions: [] },
  ...overrides,
});

const build = (
  input: ReconstructionObligationLedgerInput,
): ReconstructionObligationLedger => {
  const parsed = resolveReconstructionObligationLedgerRequest(input);
  if (!parsed.ok) throw parsed.error;
  const result = buildReconstructionObligationLedgerEvidenceValidated(parsed.value);
  if (!result.ok) throw result.error;
  return reconstructionObligationLedgerSchema.parse(result.value.normalized_result);
};

const originalCases = (
  obligation: ReconstructionObligationLedger["obligations"][number],
  evidenceId: string,
) =>
  obligation.required_case_kinds.map((kind) => ({
    kind,
    evidence_id: evidenceId,
    location: `/normalized_result/cases/${kind}`,
  }));

const reviewed = (
  id: string,
  evidenceId: string,
  overrides: Partial<ReviewedReconstructionObligation> = {},
): ReviewedReconstructionObligation => ({
  obligation_id: id,
  obligation_version: 1,
  title: `Reviewed obligation ${id}`,
  application_layer: "other",
  family: "reviewed",
  target: {
    artifact_sha256: null,
    application_node_id: null,
    semantic_node_id: null,
    location: `/reviewed/${id}`,
  },
  required: true,
  required_case_kinds: ["positive"],
  required_original_authority: "static",
  required_fixture_authority: "unit",
  required_verifier_authority: "unit",
  requires_parser_type: false,
  dependency_obligation_ids: [],
  residual_unknown_ids: [],
  unavailable_authority: [],
  required_next_evidence: ["Bind an owner and verifier."],
  disposition: "active",
  review_evidence_ids: [evidenceId],
  ...overrides,
});

const completeBinding = (
  obligation: ReconstructionObligationLedger["obligations"][number],
  evidenceId: string,
) => ({
  obligation_id: obligation.obligation_id,
  owner: {
    module_path: "fixture/owner.ts",
    symbol: "verify",
    owner_sha256: "a".repeat(64),
  },
  parser_type: null,
  original_cases: originalCases(obligation, evidenceId),
  fixtures: obligation.required_case_kinds.map((kind) => ({
    fixture_id: `fixture.${kind}`,
    case_kind: kind,
    authority: "packaged-process" as const,
    evidence_ids: [evidenceId],
  })),
  verifier: {
    verifier_id: "verifier.fixture",
    claim_id: "claim.fixture",
    command: "fixture-verifier",
    authority: "packaged-process" as const,
    status: "pass" as const,
    result_evidence_id: evidenceId,
    enumerated_obligation_ids: [obligation.obligation_id],
    nondeterminism: {
      mode: "total-order" as const,
      specification: "Fixture execution is ordered.",
    },
  },
});

describe("independent semantic vectors vs executable REA", () => {
  it("complete packaged-process vector closes", () => {
    const capture = processEvidence();
    const initial = build(request([capture]));
    const obligation = initial.obligations[0];
    if (!obligation) throw new Error("missing generated obligation");

    const p = proof("complete", obligation.obligation_id);
    const b = completeBinding(obligation, p.evidence_id);
    b.original_cases = originalCases(obligation, capture.evidence_id);

    const result = build(
      request([capture, p], {
        manifest: { bindings: [b], contradictions: [] },
      }),
    );

    console.log("COMPLETE_VECTOR_DIAGNOSTICS", JSON.stringify(result.obligations[0]));
    console.log("COMPLETE_VECTOR_LEDGER_STATUS", result.status);

    expect(result.obligations[0]?.status).toBe("verified");
    expect(result.status).toBe("ready");
  });

  it("missing original negative/cancellation cases stays open", () => {
    const capture = processEvidence();
    const initial = build(request([capture]));
    const obligation = initial.obligations[0];
    if (!obligation) throw new Error("missing generated obligation");
    const p = proof("missing-cases", obligation.obligation_id);

    const b = completeBinding(obligation, p.evidence_id);
    b.original_cases = obligation.observed_cases;

    const result = build(
      request([capture, p], {
        manifest: { bindings: [b], contradictions: [] },
      }),
    );

    expect(result.obligations[0]?.status).toBe("implemented");
    expect(result.status).toBe("open");
    expect(result.obligations[0]?.diagnostics.map((d) => d.code)).toEqual(
      expect.arrayContaining(["missing-original-case"]),
    );
  });

  it("weak proof authority stays open", () => {
    const capture = processEvidence();
    const initial = build(request([capture]));
    const obligation = initial.obligations[0];
    if (!obligation) throw new Error("missing generated obligation");
    const p = proof("weak", obligation.obligation_id);

    const b = completeBinding(obligation, p.evidence_id);
    b.fixtures = b.fixtures.map((f) => ({ ...f, authority: "unit" as const }));
    b.verifier = { ...b.verifier, authority: "unit" as const };

    const result = build(
      request([capture, p], {
        manifest: { bindings: [b], contradictions: [] },
      }),
    );

    expect(result.obligations[0]?.status).toBe("implemented");
    expect(result.status).toBe("open");
  });

  it("residual unknown stays unknown", () => {
    const id = "obl.unknown";
    const p = proof("unknown", id, "shipped-artifact");
    const o = reviewed(id, p.evidence_id, {
      residual_unknown_ids: ["u1"],
    });

    const b = {
      obligation_id: id,
      owner: {
        module_path: "fixture/owner.ts",
        symbol: "verify",
        owner_sha256: "b".repeat(64),
      },
      parser_type: null,
      original_cases: [
        {
          kind: "positive" as const,
          evidence_id: p.evidence_id,
          location: "/positive",
        },
      ],
      fixtures: [
        {
          fixture_id: "fixture.positive",
          case_kind: "positive" as const,
          authority: "unit" as const,
          evidence_ids: [p.evidence_id],
        },
      ],
      verifier: {
        verifier_id: "verifier.unknown",
        claim_id: "claim.unknown",
        command: "fixture-verifier",
        authority: "unit" as const,
        status: "pass" as const,
        result_evidence_id: p.evidence_id,
        enumerated_obligation_ids: [id],
        nondeterminism: {
          mode: "total-order" as const,
          specification: "ordered",
        },
      },
    };

    const result = build(
      request([p], {
        reviewed_obligations: [o],
        manifest: { bindings: [b], contradictions: [] },
      }),
    );

    expect(result.obligations[0]?.status).toBe("unknown");
    expect(result.status).toBe("unknown");
  });

  it("dependency chain fails closed", () => {
    const p = proof("deps", "obl.a", "shipped-artifact");
    const ids = ["a", "b", "c"];
    const ros = ids.map((id, i) =>
      reviewed(`obl.${id}`, p.evidence_id, {
        dependency_obligation_ids:
          i === 0 ? ["obl.b"] : i === 1 ? ["obl.c"] : ["obl.missing"],
      }),
    );

    const bindings = ros.map((o) => ({
      obligation_id: o.obligation_id,
      owner: {
        module_path: "fixture/owner.ts",
        symbol: "verify",
        owner_sha256: "c".repeat(64),
      },
      parser_type: null,
      original_cases: [
        {
          kind: "positive" as const,
          evidence_id: p.evidence_id,
          location: "/positive",
        },
      ],
      fixtures: [
        {
          fixture_id: `fixture.${o.obligation_id}`,
          case_kind: "positive" as const,
          authority: "unit" as const,
          evidence_ids: [p.evidence_id],
        },
      ],
      verifier: {
        verifier_id: `verifier.${o.obligation_id}`,
        claim_id: `claim.${o.obligation_id}`,
        command: "fixture-verifier",
        authority: "unit" as const,
        status: "pass" as const,
        result_evidence_id: p.evidence_id,
        enumerated_obligation_ids: [o.obligation_id],
        nondeterminism: {
          mode: "total-order" as const,
          specification: "ordered",
        },
      },
    }));

    const result = build(
      request([p], {
        reviewed_obligations: ros,
        manifest: { bindings, contradictions: [] },
      }),
    );

    expect(result.obligations.map((o) => o.status)).toEqual([
      "blocked",
      "blocked",
      "blocked",
    ]);
    expect(result.status).toBe("open");
  });


  it("contradiction duplicate-evidence boundary is observable", () => {
    const p = proof("duplicate-contradiction", "obl.duplicate-contradiction");
    const original = createEvidence(
      undefined,
      { id: "fixture-static", name: "Static artifact", version: "1" },
      {
        predicateType: "rea.static-observation",
        operation: "observe_static_behavior",
        parameters: {},
        result: { value: "original" },
        confidence: "observed",
        authority: "shipped-artifact",
      },
    );
    const o = reviewed(
      "obl.duplicate-contradiction",
      original.evidence_id,
      {
        required_original_authority: "static",
      },
    );
    const b = {
      ...completeBinding(
        {
          obligation_id: o.obligation_id,
          required_case_kinds: o.required_case_kinds,
        } as ReconstructionObligationLedger["obligations"][number],
        p.evidence_id,
      ),
      original_cases: [
        {
          kind: "positive" as const,
          evidence_id: original.evidence_id,
          location: "/positive",
        },
      ],
    };

    const result = build(
      request([p, original], {
        reviewed_obligations: [o],
        manifest: {
          bindings: [b],
          contradictions: [
            {
              obligation_id: o.obligation_id,
              evidence_ids: [original.evidence_id, original.evidence_id],
            },
          ],
        },
      }),
    );

    const status = result.obligations[0]?.status;
    const diagnostics = result.obligations[0]?.diagnostics.map((d) => d.code);
    console.log(
      "DUPLICATE_CONTRADICTION_BOUNDARY",
      JSON.stringify({ status, diagnostics }),
    );
    expect(status).toBe("contradicted");
    expect(diagnostics).toContain("contradiction");
  });

  it("candidate generation preserves cancellation and truncation uncertainty", () => {
    const base = EMPTY_PROCESS_CAPTURE_EXAMPLE;
    const captured = {
      ...base,
      exit: {
        ...base.exit,
        code: null,
        signal: 15,
        reason: "exited" as const,
      },
      truncated: true,
      limitations: ["synthetic truncation for completeness vector"],
      residual_unknowns: [
        { scope: "process" as const, reason: "synthetic residual unknown" },
      ],
    };

    const evidence = createEvidence(undefined, PROCESS_PROVIDER, {
      predicateType: "rea.process-capture",
      operation: "capture_process_scenario",
      parameters: {},
      result: jsonValueSchema.parse(processCaptureSchema.parse(captured)),
      confidence: "observed",
      authority: "controlled-replay",
    });

    const result = build(request([evidence]));
    expect(result.obligations.length).toBeGreaterThan(0);

    const obligation = result.obligations[0];
    expect(obligation?.required_case_kinds).toEqual([
      "positive",
      "negative",
      "cancellation",
      "teardown",
    ]);
    expect(obligation?.observed_cases.map((c) => c.kind)).toEqual(
      expect.arrayContaining(["negative", "cancellation", "teardown"]),
    );
    expect(result.limitations.join(" ")).toContain("truncated");
    expect(obligation?.status).toBe("unknown");
    expect(result.status).toBe("unknown");
  });
});

// Hosted execution probe: output counts only from the exact frozen upstream implementation and vector set.
