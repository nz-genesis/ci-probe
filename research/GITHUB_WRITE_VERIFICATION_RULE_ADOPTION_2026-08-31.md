# GitHub Write Verification Rule Adoption — 2026-08-31

## Purpose

Record adoption of the Genesis repository write-verification rule in the executable research apparatus.

## Rule

A GitHub write is not reported as committed/created/updated/verified until the resulting object is re-fetched and its expected identity, state, content, and resulting commit are checked.

## Required evidence chain

write operation → returned identifier → GitHub re-fetch → state/content verification → report

For workflows, the chain additionally requires exact workflow/run association and completed conclusion when execution is part of the claimed evidence.

## Negative rule

Tool-returned commit SHA alone is not sufficient evidence for the report. If post-write verification is unavailable, status remains UNVERIFIED/PENDING.

## Scope

Files, commits, issues, pull requests, branches, workflows, tags, and other GitHub objects used by ci-probe or Genesis research.

## Status

Adopted as a research integrity requirement. This record does not itself claim hosted execution of any research probe.
