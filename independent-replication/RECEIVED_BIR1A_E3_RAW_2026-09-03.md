# Clean-Room Independent Semantic Reconstruction

## 1. Scope and assumptions

This is an independent reconstruction from the frozen IR-V2 challenge and the
public execution packet only. I treat a semantic basis as the smallest set of
irreducible distinctions needed to answer the stated reconstruction obligations,
not as a preferred database schema or programming API.

Assumptions:

- Reconstruction means answering bounded future questions from finite retained
  records.
- External reality, internal observations, and normative authorization are
  different things.
- "Unknown" is a first-class epistemic status and is not failure.
- A relation or attribute counts as semantic only when its interpretation is
  specified; opaque payloads and unrestricted predicates cannot hide distinctions.
- Minimality below is a local irreducibility claim for this corpus, not a proof of
  global or universal minimality.

## 2. Independently derived semantic distinctions

The obligations require these distinctions:

1. A present condition is not the occurrence that produced it.
2. Technical ability is not permission or legitimacy.
3. An attempt is not an achieved external effect.
4. A received signal is not the external fact it purports to report.
5. Unknown outcome is not success and is not failure.
6. Identity continuity can survive a change in observable condition.
7. Equal present conditions can have different causal histories.
8. Validity and authority can be time-scoped.
9. Causal precedence is not an unjustified total ordering; concurrency must be
   representable.
10. Composition of occurrences does not by itself create a new irreducible kind.

The distinctions are semantic obligations, but they need not each be a primitive.
For example, failure can be derived as a status of an assertion or condition,
and concurrency can be derived as the absence of a precedence edge.

## 3. Independently derived basis

### B1. Referent and continuity

An identifiable entity, role, resource, or process, with a relation saying which
later records concern the same continuing referent.

- Obligation: distinguish identity continuity from changing observable condition.
- Semantic or implementation: semantic. A database primary key is only one
  implementation; the sameness relation is needed for reconstruction.

### B2. Condition

A time-scoped state, property, or observable configuration associated with a
referent or system.

- Obligation: represent present conditions and before/after states.
- Semantic or implementation: semantic. A field, snapshot, or predicate can
  implement it, but cannot remove the state/change distinction.

### B3. Occurrence

An action, attempt, transition, transformation, communication, receipt,
modification, crash, retry, or external interaction, linked to participants and
possibly to conditions.

- Obligation: preserve what happened as an occurrence separately from what is
  currently true.
- Semantic or implementation: semantic. An event table is optional, but the
  occurrence distinction is not.

### B4. Normative and enabling constraint

Prerequisites, technical capability, permission, prohibition, authority,
validity, and applicability conditions governing an occurrence, each scoped to
the relevant referent and time.

- Obligation: distinguish possibility from permission and stale authority from
  current authority.
- Semantic or implementation: semantic. A policy engine is implementation; the
  normative distinction is required.

### B5. Assertion and epistemic status

A system-held claim about a condition or occurrence, including source,
observation/receipt context, time, scope, and status such as established,
contradicted, or unresolved.

- Obligation: distinguish information from truth, observation from world state,
  and unknown result from success or failure.
- Semantic or implementation: semantic. A boolean "success" field is
  insufficient because it collapses source and uncertainty.

### B6. Temporal-causal structure

Intervals, temporal validity, causal links, precedence, and concurrency among
referents, conditions, occurrences, constraints, and assertions.

- Obligation: reconstruct history, preserve validity windows, and avoid inventing
  order where only concurrency is justified.
- Semantic or implementation: semantic. Physical timestamps are not enough for
  causality, and a total sequence is too strong when evidence is partial.

## 4. Mapping every challenge case to the basis

| Case | Basis | Reconstruction |
|---|---|---|
| C01 | B2, B3, B6 | Store initial/result conditions and the occurrence linking them. |
| C02 | B3, B4 | Capability enables an occurrence while a separate constraint decides permission. |
| C03 | B3, B4, B5 | Record prerequisites, attempt, and whether the intended external result is established. |
| C04 | B3, B6 | Keep concurrent occurrences incomparable unless precedence is evidenced. |
| C05 | B3, B5 | Receipt is an occurrence carrying an assertion, distinct from the external event. |
| C06 | B3, B5, B6 | Preserve process termination and unresolved external outcome. |
| C07 | B3, B4, B6 | Record the governed modification, its authority, and durable bounded links. |
| C08 | B3, B4, B5 | Retention of input does not prove source, validity, or authorization. |
| C09 | B1, B2, B3 | Link the same referent across transformation and changed condition. |
| C10 | B1, B3, B6 | Preserve differing preceding occurrences even when current condition is equal. |
| C11 | B4, B5, B6 | Evaluate information/permission against its time interval and status. |
| C12 | B3, B6 | Compose occurrences and relations without adding a combination primitive. |

The adversarial cases A01-A08 exercise, respectively, history, report/fact and
effect distinction, concurrency, authority, assertion error, unresolved
outcome, continuity, and input-versus-permission.

## 5. Removal analysis

### Remove B1

Lost: C09, C10, A01, A07. A changed condition can no longer be recognized as
belonging to the same continuing referent. B2 plus B3 cannot reconstruct
sameness without importing an untyped hidden identity relation. This is a
semantic loss, not merely an implementation inconvenience.

### Remove B2

Lost: C01, C09, C10, A01, A07. There is no semantic object for current,
previous, or resulting condition. B3 alone can say an occurrence happened, but
not what condition it changed.

### Remove B3

Lost: C01, C03, C04, C05, C06, C07, C08, C12. Conditions and assertions cannot
express an attempt, receipt, transformation, modification, crash, or external
interaction without treating an occurrence as an opaque payload. That would
launder the required distinction.

### Remove B4

Lost: C02, C03, C07, C08, C11, A04, A08. Technical capability, prerequisites,
permission, and temporal authority collapse. Encoding them as arbitrary
attributes does not reconstruct normative force unless the missing constraint
semantics is reintroduced.

### Remove B5

Lost: C03, C05, C06, C08, C11, A02, A05, A06. The model cannot distinguish a
received report from world state or preserve an unresolved outcome. B2 cannot
stand in for B5 because a system's belief is not the external condition.

### Remove B6

Lost: C04, C06, C07, C10, C11, A03. Causality, temporal validity, and
concurrency disappear. A total log is not a reduction: it adds unsupported
ordering and can change valid reconstructions.

No B1-B6 element is removable for this corpus without moving its semantic force
into an opaque payload, unrestricted predicate, or unstated interpreter.

## 6. Merge and factorization analysis

- B1 plus B2 cannot be safely merged. "Same referent" and "same condition" are
  independent: an object can persist while its condition changes, and two
  objects can share a condition.
- B2 plus B3 cannot be merged. A condition is a time-scoped property; an
  occurrence is an occurrence in time. Equal endpoint conditions do not identify
  the change.
- B3 plus B5 cannot be merged. A signal can be received when the external event
  is false, and equal signals can precede different effects.
- B4 plus B5 cannot be merged. Permission is normative; an assertion reports
  information and may be wrong.
- B4 plus B6 cannot be merged. A rule may be valid during an interval, while
  temporal order and causality concern events and evidence.
- B5 plus B6 cannot be merged. An assertion has a temporal scope, but the
  assertion/fact distinction remains even with perfect clocks.
- B3 plus B6 can be implemented as an event graph, but that graph still
  semantically contains both occurrences and their ordering relations; the
  apparent merge is representational, not a reduction.

Removed named categories:

- success and failure: statuses of B2/B5, not new primitives;
- message and signal: B3 plus B5;
- retry and crash: B3 occurrences with B6 links;
- concurrency: a B6 relation or absence of precedence;
- transaction or workflow: composition of B3 records and B6 relations;
- history log: a retention policy over B3/B6, not a semantic primitive.

## 7. Strongest counterexamples against the basis

1. **Irreversible payment with lost acknowledgement.** A request is attempted,
   the payer may be charged, and the worker crashes before confirmation. A model
   without B5 cannot preserve "possibly realized"; a model without B3 cannot
   distinguish request, retry, and charge.
2. **Duplicate retry.** The first request succeeds but its acknowledgement is
   lost; a retry also succeeds or is rejected as duplicate. Treating the
   request as a state transition loses multiplicity and idempotency evidence.
3. **Conflicting sensors.** Two reports disagree about an external fire. A
   report/fact distinction and source-scoped assertions are needed; a single
   condition is insufficient.
4. **Distributed writes.** Two replicas converge to the same bytes through
   different writes with no cross-replica order. A total sequence loses valid
   causal alternatives.
5. **Revoked authority.** A capability remains technically usable after policy
   revocation. B4 must represent both ability and current permission.
6. **Self-modification.** A service changes its own policy and then evaluates an
   operation under the new policy. Identity, occurrence, temporal validity, and
   causal links must survive the change.
7. **Mathematical history.** Two derivations yield the same theorem but differ in
   assumptions. The conclusion alone cannot answer which premises or proof
   occurrence led to it; B3/B6 retain provenance.

The strongest attack is that B1 may be derivable from stable keys and B6 may be
derivable from an event calculus. That is a choice of a richer formalism, not a
demonstrated removal: the semantic content still has to be supplied somewhere.

## 8. Three independently generated heterogeneous cases

### H1 - Distributed inventory reservation

Two warehouses receive concurrent reservations for the same SKU. Both local
systems can technically reserve, but only one has current authority after a
quota change. One acknowledgement is lost and a retry may duplicate the
reservation.

- Required distinctions: B2/B3 for inventory and attempts; B4 for quota and
  authority; B5 for acknowledgements and unresolved realization; B6 for
  concurrency and retry causality.
- Representation: referent-scoped inventory conditions, reservation
  occurrences, time-scoped policy constraints, source-scoped assertions, and a
  partial causal graph.
- Possible reduction: one event graph with typed nodes can encode all of this,
  but the node/edge types retain the six semantic distinctions.
- Strong counterexample: if the first reservation realized but its signal was
  lost, a retry can oversell; collapsing signal into effect produces the wrong
  inventory history.

### H2 - Physical laboratory intervention

An instrument is commanded to heat a sample. The command is permitted, the
heater attempt occurs, power is interrupted, and the final temperature is not
measured. The sample remains the same sample but its observable condition may
have changed.

- Required distinctions: B1/B2 for sample continuity and temperature; B3 for
  command, attempt, interruption; B4 for safety permission; B5 for missing
  measurement; B6 for temporal sequence.
- Representation: one sample referent, condition intervals, command and
  interruption occurrences, safety constraint, and an unresolved temperature
  assertion.
- Possible reduction: encode every item in a physical trace. That trace still
  needs a semantic marker for identity, attempted action, and unmeasured result.
- Strong counterexample: assuming no measurement means no heating confuses
  unknown effect with failure.

### H3 - Mathematical proof with changing assumptions

A theorem is derived under axiom set A, then the same conclusion is derived
under stronger axiom set B. The present theorem text is equal, but the preceding
assumptions differ and B becomes invalid after a time-indexed revision.

- Required distinctions: B2 for present theorem/assumption conditions; B3 for
  derivations; B5 for claims of validity; B6 for proof dependency and revision;
  B4 for applicability of axioms.
- Representation: theorem referent and condition, derivation occurrences,
  premise/authority constraints, validity-scoped assertions, and dependency
  partial order.
- Possible reduction: store only the theorem and a proof hash. This loses which
  assumptions established it and whether they remain applicable.
- Strong counterexample: identical theorem text under incompatible assumptions
  demonstrates that current output alone does not preserve causal provenance.

## 9. Challenge omissions and limitations

- It gives no formal representation language or reconstruction queries.
- "Smallest" has no metric: primitive count, definability, information content,
  or implementation cost could yield different answers.
- It does not define entity sameness, externality, result, validity, or evidence
  sufficient to resolve uncertainty.
- It underrepresents irreversible effects, acknowledgement loss, retry,
  duplicate realization, idempotency, compensation, and recovery.
- It has little explicit conflict, deception, authentication, or multi-party
  authority.
- It does not test resource identity, granularity, nesting, or deletion.
- C07 does not state the bound or retention policy for "without an unbounded
  execution log."
- C10 makes retention query-dependent ("when required by the task") without
  specifying the task.
- The cases bias attention toward event/history, authority, and epistemic
  distinctions; other domains might expose additional irreducibles.
- A finite bounded corpus cannot establish a universal finite basis. Outside
  the corpus, there may be no finite basis for all semantic domains.

Therefore the challenge supports a coverage argument and exposes several
necessary distinctions, but it cannot defensibly establish a unique global
minimal basis.

## 10. Temporal and concurrency analysis

Physical timestamps alone cannot establish causality, and logical sequence
numbers can invent order. B6 should support intervals and a partial order:
`a precedes b`, `a overlaps b`, `a caused b`, or no justified relation. A retry
must be a new B3 occurrence linked causally to the earlier attempt, not an
overwrite. A crash ends a process occurrence but does not determine the
external result. Validity of B4/B5 items is an interval property and may be
revoked or superseded.

## 11. Authority and normative analysis

Capability answers "can this component technically execute?" Permission answers
"is execution allowed under the applicable rule?" Legitimacy may also depend on
issuer, scope, delegation, conflict resolution, and effective time. These are
not derived from the mere receipt of an input. The constraint semantics must be
explicit; storing a policy blob without an interpreter merely launders it.

## 12. Epistemic and uncertainty analysis

Assertions need source, time, scope, and status. A received signal can be false;
an absent signal can coexist with a realized effect. "Unknown" can later become
established or contradicted, so it is not a terminal failure state. Confidence
values alone do not replace a fact/report distinction.

## 13. External-world and effect analysis

The model must allow an occurrence to be sent, partially executed, realized,
rejected, duplicated, compensated, or left unresolved. External effect is not
identical to local state, local acknowledgement, or process termination.
Irreversible effects make this distinction material: replay can create a second
effect even when local state appears unchanged.

## 14. Semantic versus implementation distinction

Tables, logs, hashes, opaque payloads, predicates, types, and event graphs are
implementation choices. They count as reductions only if the remaining formal
semantics can reconstruct the same distinctions without hidden conventions.
Putting permission in an arbitrary attribute, truth in a boolean, identity in an
unstated key convention, or causality in log order is not a valid reduction.

## 15. Alternative bases considered

1. **Five-element basis:** merge B1 with B2 as "entity trajectory." Rejected:
   equal condition does not imply equal identity, and continuity through changed
   condition is a required distinction.
2. **Five-element basis:** merge B5 with B6 as "time-indexed knowledge."
   Rejected: knowledge about a fact and temporal ordering among world
   occurrences are different even with perfect timestamps.
3. **Four-element event calculus:** entities, events, rules, and labels. This
   can encode the corpus only by making labels/rules carry the full assertion,
   condition, and temporal semantics; that is anti-laundering, not reduction.
4. **State-transition-only basis:** rejected by C01, C05, C06, C10, and
   irreversible-effect cases because transitions do not preserve reports,
   attempts, unresolved outcomes, or causal alternatives.
5. **No finite basis:** possible as a claim about unrestricted universal
   semantics, but too strong for the bounded challenge; six elements are a
   sufficient local basis here.

## 16. Unresolved questions

- What exact queries must reconstruction answer?
- Is identity extensional, legal, physical, or application-defined?
- What evidence turns an unresolved external result into established fact?
- Are validity intervals monotonic, revocable, or versioned?
- What finite retention bound is required by C07?
- Must contradictory assertions coexist, and how are they adjudicated?
- Does minimality mean semantic definability or implementation complexity?

## 17. Confidence and epistemic status

- Observed: the challenge text contains the stated case obligations and
  adversarial requirements; the supplied SHA-256 was verified.
- Derived: B1-B6 cover those obligations and each has a local removal residue.
- Hypothesis: no element can be globally eliminated in a richer, explicitly
  typed formalism without relocating its semantic force.
- Unknown: whether another formalism yields a smaller basis under a different
  minimality metric.
- Not claimed: global minimality, universal completeness, or correctness by
  agreement with any other reconstruction.

## 18. Provenance

- participant_id: `ai-assistant-copilot-sdk-vscode`
- model/provider: not exposed by execution interface
- runtime/version: VS Code Copilot SDK; exact version not exposed
- challenge_id: `IR-V2`
- exact challenge revision: `7facfe9a7fe4b0857b0c0243b4b90ae50a384829`
- challenge SHA-256: `03b25456a1ad0b40272daa1ca633910855433cfdce6ece8d0cf9e3352cd7ef1b`
- execution start UTC: `2026-09-03T11:33:03Z`
- execution end UTC: `2026-09-03T11:34:10Z`
- prior Genesis exposure: `unknown`
- relationship to Genesis operator: `unknown`
- raw-report SHA-256: `to be computed after freeze`
- commitment SHA-256: `not supported; no commitment endpoint or nonce protocol was available`

## 19. Candidate-visibility statement

Before freezing this report I did not inspect Genesis Lab, private Genesis
research, previous external results, Genesis hypotheses, expected answers, or
repository history for Genesis research. No external interpretation was used.

## 20. Exact challenge SHA-256

`03b25456a1ad0b40272daa1ca633910855433cfdce6ece8d0cf9e3352cd7ef1b`
