# Execution Scenario Matrix

## Scope

This is a public, project-agnostic experimental fixture. It records only generic execution observations and safe test cases. It is not a product architecture specification.

## Scenarios

| Scenario | Expected classification | Effect certainty | New-operation retry candidate |
|---|---|---|---:|
| Admission followed by revocation before execution | rejected | no effect confirmed | no |
| Successful native execution | executed → verified | confirmed | no |
| Partial external effect | partial → unknown | partial | no |
| Lost acknowledgement | unknown pending reconciliation | possible | no |
| Failure before external effect | failed | no effect confirmed | yes, after new identity and fresh admission |
| Failure after possible external effect | failed | possible | no |
| Reconciliation confirms not applied | reconciled | no effect confirmed | yes, after new identity and fresh admission |
| Reconciliation remains unresolved | unresolved | possible | no |

## Boundary rules

- Admission does not imply execution.
- Execution does not imply effect.
- Executor acknowledgement does not by itself imply authoritative verification.
- unknown is not equivalent to failed and is never sufficient for blind retry.
- A failed status alone does not establish absence of external effect.
- A new-operation retry candidate is not permission to reuse the same operation identity; it requires a new identity and fresh admission.
- Cancellation is not evidence that an external effect did not occur.
- The public matrix must not contain private project hypotheses, architecture, credentials, datasets, internal endpoints or canonical decisions.

## Evidence status

The dedicated workflow runs the root generic action-contract test module and this scenario-matrix test module. The repository smoke workflow independently runs the root action-contract module. A workflow result proves only the tests actually executed at its exact commit and job.

The probe has no persistence, network, provider integration, external side effect or real authorization authority. Its observations do not prove a private system's implementation or acceptance.


## Reproducible execution evidence — 2026-11-07

- Source commit under test: 91d622f224a298cd3b010862cb61f97e2245143c.
- Workflow: https://github.com/nz-genesis/ci-probe/actions/runs/42382451041
- Job: generic-execution-scenarios, job ID 128432736252.
- Result: SUCCESS; runner log reports Ran 23 tests and OK.
- Executed suites: root test_action_probe.py plus action_probe/test_scenario_matrix.py.
- Runner: GitHub-hosted ubuntu-latest; Python 3 runtime selected by runner default (no explicit version pin in this workflow).
- The workflow checked out the branch commit shown above and completed the documentation-presence check.

This is a generic fixture/model test result only. It does not establish private Web2API implementation behavior, real provider permission, physical computer effects, durable recovery, concurrency safety or production acceptance. Unrelated branch-push workflow runs are not included in this evidence claim.
