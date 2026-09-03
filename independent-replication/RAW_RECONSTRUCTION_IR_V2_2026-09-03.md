# Independent semantic reconstruction — IR-V2

Status: frozen raw report. No Genesis candidate, BIR result, E3 result, Red-Team
conclusion, comparison matrix, or issue discussion was consulted before this
report was frozen. This report is a factorisation of the published neutral
challenge, not a claim about any private ontology.

## 1. Input integrity

- Challenge: `IR-V2`, `independent-replication/challenge-v2.json`
- Repository revision from which the bytes were obtained: `d71cc444622776aaab726a73b7123765f20ea9e6`
- Challenge SHA-256: `03b25456a1ad0b40272daa1ca633910855433cfdce6ece8d0cf9e3352cd7ef1b`
- Challenge byte count: `3513`
- Published packet digest: `03b25456a1ad0b40272daa1ca633910855433cfdce6ece8d0cf9e3352cd7ef1b`
- Integrity result: `PASS`

The execution packet did not name an origin commit. The revision above is the
exact checked-out revision used to obtain bytes whose content digest matches
the packet. It is recorded as provenance, not substituted for the content
digest.

Only the active challenge, its public execution packet, and its representation
contract were read. The historical V1 challenge and BFV control surface were
not used as semantic evidence.

## 2. Semantic obligations extracted from IR-V2

The cases require the following independently stated obligations:

1. A change has a resulting condition and a reconstructable occurrence.
2. Technical ability and normative permission can differ.
3. Operations have prerequisites; attempts can occur without establishing the
   intended external result.
4. Concurrent changes need not have a fabricated total order.
5. A received signal is not the outside event it describes.
6. Loss of a process can leave an external result unresolved.
7. A governed modification remains reconstructable without an unbounded log.
8. Received input can be retained while source, validity, and authority remain
   unresolved.
9. An entity can continue through a transformation while its condition changes.
10. Equal current conditions can retain distinct preceding circumstances.
11. Applicability can depend on time; stale information must not become current
    fact silently.
12. Composition of operations does not itself create a new irreducible category.

The eight published adversarial cases restate these obligations as collisions:
same condition/different history, same signal/different external result,
concurrency, capability/authority, evidence/truth, crash uncertainty,
transformation/continuity, and received-input/permission.

## 3. Candidate factorisation

The following eight factors are the smallest factorisation I found that keeps
all distinctions explicit under the contract. “Smallest” here means no smaller
tested factorisation was found for this finite corpus; it is not a universal
minimality claim.

### F1 — Referent continuity

A tracked referent and its continuity relation across representations or
transitions. The relation may be one-to-one, merged, split, transformed, or
unknown; it is not equality of current condition. This factor handles
continuity, identity merge/split, and “same present condition, distinct
referents/history”.

### F2 — Condition

An admissible state/value of a referent or relevant external system at a
specified validity context. A condition is not an occurrence, command,
observation, permission, or causal explanation. Multiple equal condition
values may be attached to distinct referents or distinct histories.

### F3 — Operation attempt and occurrence

An operation description (including prerequisites), an attempt record, and an
occurrence record are explicit related records, not one status field:

`operation -> attempt -> occurrence`.

Either edge may be absent. An attempt records that performance was tried; an
occurrence records that an event happened. The occurrence may have no operation
parent (autonomous change), and an operation may have no attempt or occurrence.
This factor does not assert an external effect.

### F4 — External realisation/effect

The externally situated transition or changed condition produced by an
occurrence, including zero, one, or many effects. It is independent of local
acknowledgement and can be unknown or unresolved. An occurrence can happen
without an effect; an effect can occur without a command. This is the
boundary needed to avoid treating local execution or acknowledgement as proof
of world change.

### F5 — Capability

Technical means or ability available to a component for an operation. It is
descriptive, not normative, and does not imply that performance is allowed.
Capability can be absent while permission exists, or present while permission
does not.

### F6 — Normative authority

A permission/prohibition relation over a holder, act, scope, and validity
interval, with issuer/delegation and revocation relations. Authority is
separate from capability and from an input merely being received. Scope
mismatch, expiry, revocation, and attenuation are represented by relation
arguments and temporal validity, not by an opaque modality field.

### F7 — Information and evidential support

An information artifact has content and a source/provenance. A support
relation connects an artifact to a claim or condition with a reliability or
uncertainty assessment. Thus signal, claim, evidence, provenance, conflicting
reports, delayed/stale reports, and derived conclusion remain distinguishable.
Support is not truth; a conclusion is not silently promoted to an external
condition.

### F8 — Typed temporal/causal/history relations

Explicit relations are typed at the relation level:

- temporal validity and timestamps;
- definite before/after;
- partial order;
- concurrency/incomparability;
- uncertain or contradictory ordering;
- causal dependency (including delayed effect).

Retained history is a projection of referents, occurrences, effects, and these
relations. It is not an additional primitive. A relation graph is permitted
only when the relation type and its uncertainty/provenance are explicit; a
generic relation with an undisclosed semantic label would be laundering.

## 4. Dependencies and composition rules

The core composition is:

`referent --has condition--> condition`

`operation --may satisfy prerequisites--> condition`

`operation --may be attempted by--> actor`

`attempt --may produce--> occurrence`

`occurrence --may realise--> external effect/condition transition`

`actor --has capability--> operation`

`authority holder --is permitted/prohibited for--> operation/scope`

`information artifact --reports/supports--> claim/condition`

`artifact --has provenance/validity--> source/time`

`occurrence/effect/artifact --related by--> temporal or causal relation`.

An operation sequence, plan, recovery, or multi-effect action is a graph
composition of these records. Composition does not add a factor. A projection
such as “completed”, “failed”, “unknown”, “partial”, or “stale” is materialised
only when its inputs and rule are recorded; it cannot replace the inputs.

## 5. Case coverage

| Case | Required factors | Reconstruction |
|---|---|---|
| C01 | F2, F3, F4, F8 | Before/after conditions, an occurrence, and its effect relation are separate. |
| C02 | F5, F6 | Capability and permission are independent relations. |
| C03 | F2, F3, F4 | Preconditions attach to operation; attempt and external realisation are distinct and may be unresolved. |
| C04 | F3/F4, F8 | Concurrent occurrence/effect nodes have an incomparability relation, not a false total order. |
| C05 | F4, F7 | Signal artifact and external event/effect are distinct; the signal may be wrong. |
| C06 | F3, F4, F7, F8 | Process-loss occurrence plus unknown realisation and later evidence preserves unresolved status. |
| C07 | F1-F4, F8 | Governed change is an authority-linked operation/occurrence/effect graph with finite relevant provenance. |
| C08 | F6, F7, F8 | Retained input is an artifact; source, validity, and authority can be unresolved or stale. |
| C09 | F1, F2, F3/F4 | Continuity relation survives a condition-changing transformation. |
| C10 | F1, F3/F4, F8 | Equal current conditions retain different referents or preceding graphs. |
| C11 | F6/F7, F8 | Permission and information have validity intervals; stale validity does not become current. |
| C12 | all as needed, no new factor | Sequential, parallel, and nested operations are graph composition. |

## 6. Removal tests

Each removal was tested against the stated cases and against the adversarial
collisions. No opaque catch-all field or hidden interpreter is used.

| Removed factor | Decision | Concrete loss |
|---|---|---|
| F1 continuity | KEEP | Equal present conditions cannot distinguish two referents, transformation continuity, identity merge, or split. Encoding a continuity key inside condition would hide the removed dimension. |
| F2 condition | KEEP | A transition has no reconstructable resulting state; “same condition” and “changed condition” collapse. |
| F3 attempt/occurrence | KEEP | Command-issued, attempted, and actually-occurring event collapse. An effect alone cannot say whether an attempt occurred, and an attempt cannot prove occurrence. |
| F4 external effect | KEEP | Execution without world change, world change without command, and lost acknowledgement become indistinguishable. |
| F5 capability | KEEP | “Can perform” versus “cannot perform” cannot be reconstructed from authority or occurrence; permission is not a technical mechanism. |
| F6 authority | KEEP | A capable worker, an authorized worker, a revoked worker, and a scope-mismatched worker collapse. |
| F7 information/evidence | KEEP | Signal, claim, source, reliability, conflicting evidence, and delayed/stale evidence collapse into world fact or opaque metadata. |
| F8 typed relations | KEEP | Concurrency, partial order, causal delay, validity, and distinct histories cannot be reconstructed from timestamps alone. A generic untyped relation would merely rename this factor. |

### Tested merge alternatives

- F3+F4 merged into an “action status” loses an occurrence with no effect and
  an effect with no command; KEEP separate.
- F5+F6 merged into “can-do” loses capability-without-permission and
  permission-without-capability; KEEP separate.
- F2+F4 merged into “world state” loses occurrence/effect multiplicity and
  event-without-change; KEEP separate.
- F1+F8 merged into a history identifier loses continuity through
  transformation and permits two histories to be equal merely by naming;
  KEEP separate.
- F7 merged into F2 loses false, conflicting, stale, and unresolved reports;
  KEEP separate.
- F8 split into timestamp, order, causality, and history would be a useful
  representation refinement, but not semantic necessity here: typed relations
  retain each distinction and history is derivable.

## 7. Representation versus semantics and anti-laundering

Scalar values are sufficient for individual condition values, timestamps,
reliability numbers, and uncertainty values, but not for their roles. Tuples
or records are useful for operation, authority, and evidence because their
components have explicit meanings. Relations are necessary for continuity,
permission, support, temporal order, and causality. Events/occurrences are
necessary records because “something happened” is not a state value. A graph
is a composition of typed records and relations, not a hidden ninth factor.

The following are prohibited reductions:

1. `modality = {...}` for capability, permission, validity, and revocation;
2. `status = completed/failed/unknown` without the operation, attempt, effect,
   and evidence that justify it;
3. `history_id` without the event and relation graph that gives it meaning;
4. `metadata` containing source, reliability, time, and authority without
   typed fields and relations;
5. an “interpreter” that decides whether an attempt was an effect.

Where a generic structure carries one of these dimensions, that dimension is
counted explicitly above.

## 8. Required adversarial constructions

| Scenario | Required distinction |
|---|---|
| Identical observable states / distinct referents | F1 vs F2 |
| Capability without permission | F5 vs F6 |
| Permission without capability | F6 vs F5 |
| Expired permission | F6 + F8 validity |
| Command issued but not executed | F3 operation without attempt/occurrence |
| Execution without external effect | F3 occurrence vs F4 absent effect |
| External effect without command | F4 occurrence/effect without F3 parent |
| Effect without observation | F4 without F7 artifact |
| Observation without reliable evidence | F7 artifact with weak/absent support |
| Conflicting evidence | F7 multiple support relations with incompatible claims |
| Delayed evidence | F7 + F8 artifact time versus event time |
| Stale evidence | F7/F8 validity interval excludes present time |
| Unknown versus failed | F4 unresolved evidence versus established non-effect |
| Partial success | F4 one effect realised, another absent/unresolved |
| Multi-effect action | one F3 occurrence linked to several F4 effects |
| Autonomous external change | F4 effect/occurrence without command |
| Concurrent events | F8 incomparable occurrences |
| Temporal order without causality | F8 before relation without causal edge |
| Causality with delayed effect | F8 causal edge plus separate event/effect times |
| Same current state / different causal history | F1/F2 plus F8 causal graph |
| Identity merge | F1 many-to-one continuity relation |
| Identity split | F1 one-to-many continuity relation |
| Revoked authority | F6 revocation relation + F8 validity/order |
| Delegated authority | F6 delegation chain and attenuated scope |
| Authority scope mismatch | F6 act/resource/scope arguments do not match |

## 9. Temporal and causal test

A timestamp is a value attached to an event, artifact, or validity interval.
It does not itself establish order, because clocks can be skewed or intervals
can overlap. A before/after relation establishes order where justified; a
partial order permits incomparability; concurrency is the explicit
incomparability case. An uncertain or contradictory ordering claim is an
information artifact with provenance, not a silently selected order.

Causality is not reducible to temporal order: an unrelated event may be
earlier, while a delayed effect may be later but causally dependent. Inferred
causality must carry its support and uncertainty in F7. Thus generic typed
relations can represent the distinctions without separate primitive words,
but only if relation type, endpoints, validity, and support are explicit.

## 10. Epistemic test

An external fact is represented as a condition/effect (F2/F4), an observation
as an information artifact (F7), a claim as content in that artifact, evidence
as a support relation, provenance as source/derivation relations, reliability
as an assessed value, confirmation as an additional support relation, and
uncertainty as a value attached to the claim/support/order/effect judgment.
A derived conclusion is a projection with an explicit rule and retained
inputs. None of these permits an observation to become truth merely by being
recorded.

Independent variability does not by itself imply independent factors: source,
reliability, and validity are components/relations of F7/F8 unless a task
requires them to vary while all surrounding representation is fixed. The
corpus does require their distinctions, but not additional primitive classes.

## 11. Authority test

Technical possibility is F5. Permission/prohibition, holder, act, scope,
delegation, revocation, and temporal validity are F6 with F8 relations.
Received input is F7 and does not become authoritative by arrival. A
delegation chain is compositional; revocation is a later normative relation;
scope mismatch is failed relation matching. No opaque authority or modality
field is allowed.

## 12. Outcome test

Outcome is not an irreducible primitive in this corpus. It is a materialised
judgment/projection:

`outcome = project(operation, attempt, occurrence, external_effect, evidence,
                  validity, temporal/causal relations)`.

The projection must distinguish at least `not-attempted`, `attempted`,
`occurred`, `effect-established`, `no-effect-established`,
`partially-established`, and `unresolved`. “Failed” is only justified when
the specified failure rule establishes non-realisation; process loss alone
produces `unresolved`, not `failed`. If an implementation cannot state this
rule and retain its inputs, the reduction is `UNRESOLVED`, not a successful
derivation.

## 13. History test

For the finite obligations, retained history is reconstructable from F1
continuity, F3 occurrences, F4 effects, F7 evidence/provenance, and F8
temporal/causal relations. A finite relevant subgraph can be materialised as a
record for recovery or audit, but “history” adds no semantic dimension. If
history is required after deleting the events or relations, a history label is
an opaque catch-all and the reconstruction fails the contract.

## 14. Cross-domain test

The same factors cover research (claims, observations, evidence), mathematics
(derivations and support), software changes (operations, versions, effects),
system operations (attempt/effect/acknowledgement), robotics (external
realisation), distributed systems (partial order and conflicting evidence),
failure/recovery (unresolved effect and later reconciliation), governance
(authority/delegation/revocation), and self-evolution (referent continuity
through transformation). No domain-specific primitive was needed. Domain
vocabulary changes the values and relations, not the semantic factors.

## 15. H4 and minimality boundaries

The corpus establishes finite-corpus sufficiency only. It supports a bounded
claim: under the stated representation contract, the eight-factor
factorisation above covers all published cases and adversarial collisions, and
no smaller tested merge was adequate without semantic laundering.

It does not establish:

- global or universal minimality;
- that a finite universal basis exists;
- that unlisted domains introduce no additional obligations;
- that the challenge is complete;
- that the named factors are canonical.

H4 remains open: no finite universal basis is established by this corpus.
An infinite or open-ended semantic space, new relation types, or a future
obligation requiring a distinction absent here could refute universal
finiteness without refuting this bounded reconstruction.

## 16. Strongest counterexamples and unresolved alternatives

The strongest collision is identical present condition plus identical
observation while one external effect occurred and the other did not. It
requires F2, F4, and F7 and defeats state-only, observation-only, and
outcome-only encodings.

The strongest authority collision is a technically capable worker with an
expired or scope-mismatched delegated permission. It defeats both
capability-only and permission-only encodings.

The strongest history collision is equal current condition after two
concurrent, causally different transformations. It defeats state-only and
total-order encodings.

Unresolved alternatives:

1. F3 may be split into operation, attempt, and occurrence for an
   implementation with independently queried lifecycle records; the corpus
   only establishes that their distinctions must remain explicit.
2. F7 may be split into information content, provenance, and support if
   later workloads independently manipulate each; this is a representation
   refinement, not required by IR-V2.
3. F8 may be split into temporal, causal, and validity relations; one typed
   relation family is sufficient here, but an implementation may choose
   separate relation schemas.
4. If “external effect” is defined as a special occurrence subtype rather
   than a transition relation, the distinction remains necessary; the subtype
   must not hide zero/many/unresolved effect semantics.

## 17. Provenance

- Execution start (UTC): `2026-09-03T12:43:41Z` (session start; exact tool
  execution began shortly after)
- Execution end (UTC): `2026-09-03T12:48:15Z` (raw report freeze)
- Runtime: Python `3.9.6`; Darwin `25.6.0`, arm64
- Model/provider/version: Copilot SDK in VS Code; exact model/provider version
  is not exposed to this runtime
- Solver artifact: this raw report; no external solver artifact
- Prior Genesis exposure: `unknown` at model-training level; in this run the
  user prompt itself names Genesis and lists distinctions to test
- Candidate/results exposure during run: none; no Genesis Lab, candidate
  register, architecture, closure matrix, BIR, E3, Red-Team, previous reports,
  comparison matrices, or answer-bearing discussions were consulted
- Relationship to Genesis operator: `unknown`; no material external
  independence claim is made
- Commitment/reveal: not published before this response; this artifact is
  frozen locally and must not be altered before any future commitment
- Epistemic status: `RAW_BLIND_RUN; NOT_EXTERNAL_INDEPENDENCE_BY_ITSELF`

## 18. Frozen artifact digest

The exact bytes of this file are the raw report. Its final byte count and
SHA-256 are recorded in the adjacent `.sha256` sidecar, computed after the
final write and before any comparison or amendment.
