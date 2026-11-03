# Generic JSON Parser Resource Probe

**Status:** ACTIVE GENERIC PROBE  
**Scope:** CPython standard-library JSON parser materialization and process resource observations.

## Question

How do wall time and process peak resident memory change when CPython decodes dense JSON arrays and flat JSON objects at 1, 4 and 8 MiB?

## Method

- Run each case in a fresh child process to isolate its high-water RSS.
- Generate valid JSON payloads with exact UTF-8 byte sizes.
- Measure parser wall time, baseline resident memory, process peak RSS and the delta from baseline.
- Exercise both ordinary array decoding and object decoding with a duplicate-key rejection hook.
- Record Python implementation/version, platform, runner OS and triggering commit.
- Use no third-party dependencies, network access, secrets, private source or external side effects.

## Interpretation boundary

This probe establishes observations only for the exact CPython build and GitHub-hosted runner used by its workflow. It does not establish a universal memory amplification factor, a production resource budget, transport concurrency safety, or the behavior of any private application.

The reported peak RSS is process-level high-water memory, not a per-object allocation trace. Runner baseline and allocator behavior affect the measurement. Compare cases within the same run and retain the full environment identity.

No pass/fail memory threshold is asserted. A successful run means only that all six generic payloads decoded and the measurements were captured.

## Reproduction

Run:

```bash
python3 probes/json-parser-resource-probe.py
```

The experiment-specific workflow is `.github/workflows/json-parser-resource-probe.yml`. Its artifact is bound to the triggering commit SHA.

## Non-goals

- Reimplementing a JSON parser or proposing a pre-parser scanner.
- Testing application-specific node/depth limits.
- Testing private source code, private fixtures or private semantic contracts.
- Claiming transport admission, rate limiting or bounded concurrent requests.
