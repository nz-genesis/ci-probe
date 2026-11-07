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
