# Execution Scenario Matrix

## Scope

This is a public, Genesis-agnostic experimental fixture. It records only generic execution observations and safe test cases. It is not a Genesis architecture specification.

## Scenarios

| Scenario | Expected classification | Blind retry |
|---|---|---:|
| Admission followed by revocation before execution | rejected | no |
| Execution followed by independently verified observation | verified | no |
| Partial external effect | partial / unknown pending reconciliation | no |
| Lost acknowledgement | unknown pending reconciliation | no |
| Failure established before external effect | failed | potentially, subject to policy |

## Boundary rules

- Admission does not imply execution.
- Execution does not imply effect.
- An acknowledgement does not by itself imply verification.
- `unknown` is not equivalent to `failed` and is never sufficient for blind retry.
- Cancellation is not evidence that an external effect did not occur.
- This public matrix must not contain private Genesis hypotheses, architecture, credentials, datasets, internal endpoints, or canonical decisions.

## Evidence status

The matrix is an executable test fixture. Its evidence supports only the behavior explicitly exercised by the public tests. Any interpretation for Genesis belongs in the private research repository.
