# Web2API Runtime — Public Execution Surface

**Status:** ACTIVE GENERIC EXPERIMENT

This directory is a public, provider-neutral execution surface for browser-runtime experiments needed by the private `web2api-lab` project. It contains no private project source, credentials, provider sessions, private fixtures or canonical decisions.

## Purpose

Execute the same semantic BrowserRuntime acceptance primitives on public GitHub-hosted runners so that runner provisioning, browser installation and real browser behavior are independently observable.

The experiment deliberately uses a deterministic local HTTP fixture. It does **not** contact ChatGPT, Gemini, Claude or any other provider.

## Candidate matrix

- Playwright + Node.js 24
- Patchright + Node.js 24
- Playwright + Python 3.14
- Patchright + Python 3.14

Exact dependency versions are pinned in the experiment workflow/configuration and must be rechecked before canonical runtime selection.

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

This experiment does **not** establish provider authentication, provider readiness, Web2API protocol compatibility, production security, or anti-bot properties.

## Evidence rule

A configured or queued workflow is not evidence. Evidence requires a completed run, exact commit, exact job and relevant executed steps/logs/artifacts.

Results from this public surface are independent execution evidence only. They must be interpreted and imported into the private development repository with explicit provenance and epistemic scope.
