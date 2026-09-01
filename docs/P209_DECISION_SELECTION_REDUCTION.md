# P209 — Decision / Selection / Policy / Preference Reduction

## Question

Can decision, selection, policy, and preference be represented using the current seven-element Genesis candidate basis without introducing a new semantic primitive?

Basis:

- State
- Transition
- Capability
- Authority
- Observation
- Evidence
- Constraint

## Bounded scenarios

The strengthened probe tests:

- constructive selection among admissible candidates;
- preference carried explicitly in State;
- selection changed by Constraint;
- capability membership as an admissibility condition;
- unauthorized high-score candidate cannot win;
- tie/ambiguity does not become success automatically;
- policy update represented as a State transition;
- observation is not decision;
- UNKNOWN is not success;
- evidence of one realization does not become authority for another;
- malformed candidate fails closed;
- Decision/Selection/Policy/Preference are absent from the candidate basis.

## Red-Team correction

The first P209 model was not treated as closure evidence. Red Team identified two weaknesses: preference was not explicit enough as State, and capability admissibility was not explicit enough in selection. The probe was strengthened before closure and rerun on a fresh hosted commit.

## Falsifier

P209 is falsified if a decision/selection operation requires a semantic primitive outside the seven-element basis, or if policy/preference can silently widen authority, constraints, or execution scope.

## Exact hosted evidence

Public execution substrate: `nz-genesis/ci-probe`

Exact hosted SHA:

`965a69b4575355ed700c37b82185722d3083c6cf`

Run: `33532837999`

Job: `99939934336` — `public-github-hosted-execution`

Conclusion: `success`

The fetched job record shows the cumulative workflow completed successfully, including Passes 44–49, P208, and P209. The hosted log verifies `GITHUB_SHA == CHECKED_OUT_SHA == 965a69b4575355ed700c37b82185722d3083c6cf`.

P209 output:

`P209_DECISION_SELECTION_REDUCTION_PASS; assertions=11; basis_size=7; new_primitive_required=false`

## Evidence artifact

The run finalized `ci-probe-result-33532837999` (artifact `9810425916`) and `pass49-execution-evidence-965a69b4575355ed700c37b82185722d3083c6cf` (artifact `9810424978`). Artifact digests and exact hosted evidence are recorded in the private Genesis research closure.

## Semantic status

Hosted PASS is execution evidence for the probe, not proof of canonical Genesis semantic correctness. P209 supports the reduction of Decision / Selection / Policy / Preference to the seven-element candidate basis for the bounded model. It does not establish global completeness or final minimality.
