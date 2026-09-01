# P210 — Adaptive Plan / Workflow / Strategy Reduction

## Question

Can plan, workflow, strategy, sequencing, and replanning remain non-primitives when plans are represented as State values and revised through Transitions driven by Observation/Evidence under Capability/Authority/Constraint boundaries?

## Why this is new

P208 tested constructive action classes; P209 tested decision/selection/policy/preference. P210 targets the next distinct Purpose-relevant semantic concern: adaptive multi-step organization of transitions when new observations invalidate a previously selected sequence.

## Bounded scenarios

- plan represented as ordinary State data;
- sequencing as composition of Transitions;
- observation causes bounded plan revision;
- stale plan cannot override newer observation;
- plan cannot grant Authority;
- Constraint bounds replanning;
- UNKNOWN does not trigger unconditional replanning;
- Evidence does not become future execution;
- Capability and Authority remain distinct;
- unauthorized replanning fails closed;
- duplicate planned external-effect entries are data, not evidence of duplicate world effects;
- no Plan primitive is added to the seven-element basis.

## Red-Team correction

The first hosted run failed on the UNKNOWN case because the probe asserted that recording the observation could not update State revision. That assertion was stronger than the semantic contract: UNKNOWN must not trigger unconditional **plan revision**, but recording the new observation/revision in State is allowed and useful. The probe was corrected to assert the plan remains unchanged while the revision records the observation.

The failed run is retained as negative evidence; it is not counted as a P210 PASS.

## Falsifier

P210 is falsified if adaptive planning requires a semantic primitive outside:

`State + Transition + Capability + Authority + Observation + Evidence + Constraint`

or if a plan can silently expand authority, constraints, execution scope, or world-effect claims.

## Evidence protocol

The cumulative CI Probe checks out the exact triggering `GITHUB_SHA`, verifies `HEAD == GITHUB_SHA`, executes the prior cumulative probes and P210, and uploads a dedicated P210 execution artifact.

CI PASS is execution evidence for the bounded probe, not proof of Genesis semantic correctness or canonical ontology.
