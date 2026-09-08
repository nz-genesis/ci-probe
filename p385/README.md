# P385 external implementation execution surface

This directory is a public, Genesis-agnostic execution surface for the P385 research discriminator.

## Independence boundary

The public harness contains no private Genesis source, private Genesis research corpus, private prompts, private fixtures, credentials, canonical decisions, or other private Genesis material.

It freezes only public implementation lineage and public execution instructions:

- external implementation: `lucmoreau/ProvToolbox`
- frozen commit: `bbff1d7eecd15175e6be8a055f67d311e40f9f04`
- external validation module: `modules-validation/prov-validation`

The harness executes the external implementation itself. It does not copy, fork, reimplement, or modify the implementation.

## Evidence rule

A configured or queued workflow is not execution evidence. Only a completed job with an assigned runner, observable steps/logs, and a reproducible receipt counts as external runtime evidence.

Historical implementation reports, source inspection, package availability, and the existence of this harness remain lineage/setup evidence until execution is observed.

## Scope

The first gate is external implementation execution and its native validation test suite. Subsequent concordance work may add only public, source-native challenge fixtures whose semantics are frozen before any Genesis projection.

## Privacy boundary

The public repository must remain Genesis-agnostic. Private Genesis research imports public execution evidence only through explicit private adjudication and provenance; there is no automatic write-back.

## Current frozen target

`lucmoreau/ProvToolbox@bbff1d7eecd15175e6be8a055f67d311e40f9f04`
