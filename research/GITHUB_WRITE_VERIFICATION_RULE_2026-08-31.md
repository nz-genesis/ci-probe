# GitHub Write Verification Rule

Status: ACTIVE
Effective: 2026-08-31

No research report may state that a GitHub commit, issue, pull request, file, workflow, branch, or other repository element was created, updated, deleted, or verified unless the operation's result is independently re-fetched from GitHub after the write.

Required sequence: read current state → write → capture identifier → re-fetch written object → verify expected identity/state/content/parent or base/resulting commit → report. For workflow evidence, verify the exact run associated with the resulting commit and its completed conclusion.

If post-write verification cannot be completed, report UNVERIFIED/PENDING. Never infer success from a tool response alone, a neighboring commit, a local execution, or an expected state.

This applies to genesis-lab and ci-probe and to files, commits, issues, pull requests, branches, workflows, tags, and other GitHub objects used as Genesis evidence or genealogy.
