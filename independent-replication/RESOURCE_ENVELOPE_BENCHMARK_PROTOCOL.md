# Resource Envelope Benchmark Protocol

**Status:** ACTIVE EXPERIMENTAL PROTOCOL  
**Scope:** public, Genesis-agnostic independent measurement substrate

## Purpose

Measure realization-strategy economics without embedding a target Genesis ontology. This protocol is intentionally separate from frozen IR-V2 semantic reconstruction: it tests the economic claim that the preferred realization strategy can change with resource envelope while preserving a fixed quality requirement.

## Non-goals

- proving a universal semantic basis;
- proving Genesis architecture;
- declaring a universal cheapest model;
- modifying the frozen IR-V2 challenge;
- treating CI hardware as representative of all production hardware.

## Strategies

```text
reuse | compose | adapt | acquire | create
```

`cache` is not a strategy category by itself; reuse is the observable strategy. A cache hit never grants authority.

## Required controls

Each comparison must freeze:

1. task/semantic obligation;
2. success and quality criterion;
3. input corpus or workload;
4. strategy implementation;
5. model/version where applicable;
6. runtime/tool versions;
7. resource envelope;
8. warm/cold state;
9. repetition count;
10. measurement method.

## Measurements

Report a vector, not only one scalar:

```text
quality
wall_time
cpu_time
peak_memory
model_invocations
input_tokens
output_tokens
network/tool_time
control_overhead
verification_overhead
recovery_cost
cache_lookup
cache_maintenance
cache_miss_recomputation
human_attention
```

If a dimension is unavailable, report `UNMEASURED`, never zero.

## Resource envelopes

At minimum distinguish constrained, balanced and abundant envelopes. The protocol must record actual observed CPU/memory/runtime environment rather than infer it from a runner label.

## Validity rules

A strategy is admissible only if it meets the frozen quality/safety requirements. A lower-cost result with lower quality is not a win.

Pareto-incomparable results must remain incomparable unless an explicit decision policy supplies the required preference relation.

For consequential effects, cached/reused material remains input to current authorization/admission/execution; the benchmark must never interpret a previous authorization as current authority.

## Negative controls

At least one case must make reuse worse than fresh computation, and at least one case must make extra control/verification overhead measurable. This prevents confirmation-only benchmarking.

## Reproducibility

Publish:

- exact workload identifier/hash;
- exact strategy revision;
- environment metadata;
- raw measurements;
- aggregation method;
- failed/UNKNOWN runs;
- variance statistics;
- command used;
- timestamp.

A successful GitHub Actions run proves only the exact checks executed on that runner. It does not establish production-general performance.

## Independence boundary

This protocol may produce public raw measurements. Interpretation as Genesis evidence occurs outside this repository with explicit provenance and epistemic scope. Do not add private Genesis prompts, target basis, private corpus or canonical decisions here.
