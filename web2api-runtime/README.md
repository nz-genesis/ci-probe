# Web2API Runtime — Public Execution Surface

**Status:** ACTIVE GENERIC EXPERIMENT

This directory is a public, provider-neutral execution surface for browser-runtime experiments needed by the private `web2api-lab` project. It contains no private project source, credentials, provider sessions, private fixtures or canonical decisions.

## Purpose

Execute the same semantic BrowserRuntime acceptance primitives on public GitHub-hosted runners so that runner provisioning, browser installation and real browser behavior are independently observable.

The experiment deliberately uses a deterministic local HTTP fixture. It does **not** contact ChatGPT, Gemini, Claude or any other provider.

## Current candidate matrix (checked 2026-11-03)

| Candidate | Runtime / package | Status |
|---|---|---|
| Playwright Node | Node.js 24.21.0 / `playwright@1.64.1` | Active generic probe |
| Playwright Python | CPython 3.14.10 / `playwright==1.64.1` | Active generic probe |
| Patchright Node | `patchright@1.64.3` | Excluded: stock build bundles stealth/evasion changes |
| Patchright Python | `patchright==1.64.4` | Excluded: stock build bundles stealth/evasion changes |

This probe intentionally executes only Playwright. The stock Patchright build applies automation-concealment changes in its standard patch pipeline; it is not installed or executed here. A future stripped non-evasive fork would be a separate experiment requiring complete source audit and a new public scope review.

## Tested semantics

1. create an isolated persistent browser profile;
2. launch a real Chromium browser;
3. perform semantic interaction against a local page;
4. observe deterministic application state;
5. correlate a generated request identifier;
6. close and relaunch the browser using the same profile;
7. verify persisted state;
8. verify wrong-profile isolation;
9. exercise timeout/failure observation;
10. exercise closed-browser detection;
11. record timing and process-memory observations where available.

This experiment does **not** establish provider authentication, provider readiness, Web2API protocol compatibility, production security, or anti-bot properties. Its Playwright result is generic public execution evidence only; it does not prove private Web2API integration.

## Evidence rule

A configured or queued workflow is not evidence. Evidence requires a completed run, exact commit, exact job and relevant executed steps/logs/artifacts.

Results from this public surface are independent execution evidence only. They must be interpreted and imported into the private development repository with explicit provenance and epistemic scope.
