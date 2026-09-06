# IR-V3 Hash-Binding Audit — 2026-09-06

**Purpose:** independently test whether the active verifier's protocol-bound `EXPECTED_SHA256` is actually the SHA-256 of the frozen `challenge-v3.json` exact bytes.

This is an apparatus audit only. It does not modify `challenge-v3.json`, its frozen commit, or semantic challenge content.

## Trigger

A participant reported an apparent challenge SHA mismatch. Before accepting that report or changing the public apparatus, the receiving side must independently execute the existing byte-level verifier on the canonical public repository.

## Expected interpretation

The value `50f41fdc1a7d563367fb07316f2c84adc95c74a0` is known to be the Git blob object identifier exposed for `challenge-v3.json`. The active protocol currently labels the same value as the content SHA-256. This audit is intended to resolve that distinction by executing the verifier against the exact checked-out bytes on a clean hosted runner.

## Non-retroactivity

The participant's already-frozen raw result remains auxiliary apparatus evidence. This audit does not turn it into semantic evidence and does not expose any private Genesis target material.

## Required outcome

Record the hosted verifier output, especially the independently computed SHA-256 of `challenge-v3.json`, before changing the expected digest in any active document.
