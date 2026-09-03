# Clean-Room Red-Team Report: Measurement Instrument

## A. Execution metadata

- Experiment: adversarial methodological review of the neutral measurement instrument.
- Execution start: 2026-09-03T17:48:56+03:00 (task-provided start boundary; analysis began after the integrity gate).
- Execution end: 2026-09-03T17:50:25+03:00.
- Repository: `nz-genesis/ci-probe`; temporary clone only.
- Exact commit used: `b9e1dcd90ffb9bf2a398fe63f4a6475d10ead575`.
- Model/provider/runtime/version: UNKNOWN in this environment.
- Prompt-contract SHA-256: UNKNOWN (the user-supplied prompt is not a frozen file).
- Report status: raw, frozen after this file was written; no post-freeze semantic comparison performed.

Integrity gate (performed before analysis):

| Input | Bytes | SHA-256 |
|---|---:|---|
| `independent-replication/neutral-v1/challenge.json` | 6879 | `5ba2c945176d248797739890694c35f41fb9085d977f6a5e30f696054851cd85` |
| `independent-replication/neutral-v1/representation-contract-v2.md` | 7736 | `a6094eef5a75d8948d1527cc0d640530340f6d3fe2947a36c441cf176b00e08e` |
| `independent-replication/NEUTRAL_V1_EXECUTION_BRIEF_V2.md` | 4999 | `cde67488eeb6ea0cbdff2cdf0dbdc3d2d7782883f5e25f8d36c39a33fe816c5f` |

Integrity gate: PASS. All three files existed and their bytes were read only after the gate. Report byte count and digest are computed after writing and are publication metadata, not semantic input.

## B. Scope and contamination declaration

Only the three listed frozen inputs and the task prompt were used. I did not inspect `genesis-lab`, other experiment artifacts, repository history, issues, pull requests, comments, external repositories, web material, candidate vocabularies, prior results, or target-system descriptions. Prior exposure to target material: NO KNOWN EXPOSURE (operationally treated as NO). Relationship to corpus owner/operator: UNKNOWN. No attempt was made to infer the target system or a preferred ontology.

The object of review is the measurement methodology, not a semantic basis. No candidate primitive list is proposed.

## C. Claim-by-claim attack

### C1. Observation schema and elementary records

- **CLAIM ATTACKED:** Observation records can be defined directly over an observation schema without selecting ontology.
- **FAILURE MODE:** Selecting “condition”, “same”, “operation”, “rule”, “measurement”, “equipment”, “resource”, “contract”, “machine”, “approval”, “request”, “signal”, “inspection”, “document”, and “source” already selects typed entities and distinctions. “Elementary” is a granularity choice, not an observation-free fact.
- **COUNTEREXAMPLE:** One physical episode can be recorded as one record, or as an attempt, an authorization, a resource state, and a later report. Both satisfy a generic record interface but induce different independent coordinates.
- **WHY IT MATTERS:** Factorisation and minimality vary with record boundaries and typed field boundaries. The contract cannot claim ontology neutrality merely by calling fields observable.
- **SEVERITY:** HIGH
- **REPAIR:** REQUIRED

### C2. Co-reference and persistence

- **CLAIM ATTACKED:** Co-reference/persistence is an admissible neutral query.
- **FAILURE MODE:** “Same continuing service instance”, “same contract”, and “same machine” presuppose identity criteria and continuity across time; equality of observations is insufficient.
- **COUNTEREXAMPLE:** Two indistinguishable records may refer to one continuing instance or two replacements. A carrier variable can encode this only after an identity relation has been chosen.
- **WHY IT MATTERS:** A representation that retains identity is rewarded for preserving a contract-supplied semantic distinction, while a representation that treats continuity as inferred is penalized. This is hidden semantic loading, even if identity is not called a primitive.
- **SEVERITY:** HIGH
- **REPAIR:** REQUIRED

### C3. Temporal ordering and validity

- **CLAIM ATTACKED:** ORDER, MAY_ORDER, and temporal validity are directly schema-defined and representation-independent.
- **FAILURE MODE:** “Precedes”, “same interval”, “total order”, “partial/concurrent”, and “evidence sufficient” encode a theory of time, ordering, evidence, and interval applicability.
- **COUNTEREXAMPLE:** A timestamp order, causal order, process order, and externally observed order can disagree. The query algebra does not specify which one wins or whether intervals are closed, open, instantaneous, or uncertain.
- **WHY IT MATTERS:** Holdouts can test only the temporal semantics chosen by the evaluator. A representation may appear incomplete because it uses a different but coherent order model.
- **SEVERITY:** HIGH
- **REPAIR:** REQUIRED

### C4. Possible ordering and concurrency

- **CLAIM ATTACKED:** MAY_ORDER is neutral.
- **FAILURE MODE:** “Possible” can mean epistemic ignorance, physical concurrency, nondeterministic execution, or absence of a witness. These are distinct semantics.
- **COUNTEREXAMPLE:** Two events with no evidence of order may be concurrent, ordered but unobserved, or impossible to compare because clocks are incomparable. MAY_ORDER returns the same shape for incompatible interpretations.
- **WHY IT MATTERS:** The required `concurrency` property is not measured unless the contract distinguishes concurrency from missing knowledge.
- **SEVERITY:** HIGH
- **REPAIR:** REQUIRED

### C5. Consistency and compatibility

- **CLAIM ATTACKED:** CONSISTENT(x,y) is definable directly from observations.
- **FAILURE MODE:** Consistency requires a compatibility theory: logical non-contradiction, temporal compatibility, operational feasibility, legal compatibility, or source reconciliation.
- **COUNTEREXAMPLE:** “Open at t1” and “closed at t2” are consistent under change, inconsistent under persistence, and unresolved when timestamps are uncertain.
- **WHY IT MATTERS:** A generic query name can hide a domain theory and make a representation pass or fail according to an unstated oracle.
- **SEVERITY:** HIGH
- **REPAIR:** REQUIRED

### C6. Mutation and intervention

- **CLAIM ATTACKED:** MUTATE(x, delta) is an observation-schema operation.
- **FAILURE MODE:** It presupposes an action/change model, applicability, agency, counterfactual scope, and a mapping from delta to externally realized effect.
- **COUNTEREXAMPLE:** The same command can be issued, acknowledged, applied, delayed, or have no physical effect. It is not clear whether mutation denotes an attempted transition, a request, or an intervention in the world.
- **WHY IT MATTERS:** External-effect distinctions are selected by the operation semantics before representations are compared.
- **SEVERITY:** HIGH
- **REPAIR:** REQUIRED

### C7. Provenance, verification, and source reliability

- **CLAIM ATTACKED:** Source-related information is directly observable and epistemically neutral.
- **FAILURE MODE:** “Verified”, “reliable”, “unverified”, and “materially different provenance” presuppose verification procedures, trust ordering, and an epistemic policy.
- **COUNTEREXAMPLE:** A direct signal may be authentic but stale; an unverified report may be true; two sources may be independent but equally reliable. The corpus labels these distinctions without defining their semantics.
- **WHY IT MATTERS:** Provenance is not just metadata when it changes which claims count as established or retry-safe.
- **SEVERITY:** HIGH
- **REPAIR:** REQUIRED

### C8. Externally witnessed change

- **CLAIM ATTACKED:** “External fact”, “later inspection”, and “physical result” are observable neutral categories.
- **FAILURE MODE:** The distinction between world state, witness, report, and effect contains an epistemic and causal model. “Non-success” and “safe retry” add decision semantics.
- **COUNTEREXAMPLE:** A timeout followed by no signal, a negative inspection, and an authenticated rejection are different evidence states; the contract gives no formal relation among them.
- **WHY IT MATTERS:** The instrument can require preservation of distinctions whose interpretation is evaluator-provided, producing circularity.
- **SEVERITY:** HIGH
- **REPAIR:** REQUIRED

### C9. Metamorphic tests

- **CLAIM ATTACKED:** Renaming, unrelated addition, permutation, witness deletion, and duplication are representation-independent tests.
- **FAILURE MODE:** “Unrelated”, “identical”, “witness”, “irrelevant relation”, and “should not create an event” require semantic dependency and uniqueness judgments.
- **COUNTEREXAMPLE:** Duplicating an identical observation may be a duplicate transmission, a second observation, or a second event. Removing a witness may remove support while leaving a fact unchanged, or may remove the only identity anchor.
- **WHY IT MATTERS:** Metamorphic tests can be hidden oracle calls, not neutral transformations.
- **SEVERITY:** HIGH
- **REPAIR:** REQUIRED

### C10. Holdout generation

- **CLAIM ATTACKED:** A post-freeze generator that avoids predefined ontology provides target-independent holdouts.
- **FAILURE MODE:** The generator necessarily chooses transformations, pair templates, domains, and query semantics. Avoiding a named ontology does not avoid semantic targeting.
- **COUNTEREXAMPLE:** A generator sampling the same family of timeout/rejection contrasts tests the contract's preselected distinctions while appearing vocabulary-neutral. A generator sampling only field permutations misses omitted semantics.
- **WHY IT MATTERS:** Post-freeze timing blocks direct answer leakage but not target-loaded contract leakage.
- **SEVERITY:** CRITICAL
- **REPAIR:** REQUIRED

### C11. Independent authorship

- **CLAIM ATTACKED:** Independently authored representations test representation independence.
- **FAILURE MODE:** Authors can be independent in implementation while sharing the same contract, examples, query algebra, and frozen pair distinctions.
- **COUNTEREXAMPLE:** Two authors both use different encodings but both optimize for the contract's identity, epistemic, normative, and effect labels. Their agreement demonstrates compliance with a common measurement contract, not contract independence.
- **WHY IT MATTERS:** The strongest claimed independence is implementation independence only.
- **SEVERITY:** HIGH
- **REPAIR:** REQUIRED

### C12. Relations, attributes, metadata, and carriers

- **CLAIM ATTACKED:** Anti-laundering rules prevent generic mechanisms from hiding primitives.
- **FAILURE MODE:** The boundary between generic and domain-specific relation/attribute/carrier work is itself adjudicated by the evaluator. “Ordinary” identity, membership, sequence, and composition may carry continuity, order, or evidential force.
- **COUNTEREXAMPLE:** A generic relation `r(a,b)` can encode approval, causation, provenance, applicability, or refusal unless its admissible interpretation is fixed independently. A metadata field can encode the same distinction while passing a superficial field-count test.
- **WHY IT MATTERS:** Laundering can be detected only relative to a semantic oracle that decides what a relation means.
- **SEVERITY:** CRITICAL
- **REPAIR:** REQUIRED

### C13. Complexity vector

- **CLAIM ATTACKED:** A vector of vocabulary, constructors, decoder rules, relation types, payload domains, exceptions, and assumptions avoids architecture bias.
- **FAILURE MODE:** The dimensions are still architecture-loaded and incomparable across formalisms. Counting decoder rules or assumptions may penalize explicitness and reward opaque general mechanisms.
- **COUNTEREXAMPLE:** A single general relation plus a decoder rule can replace many named relation types; whether this is cheaper depends on rule language, interpreter power, and what counts as an exception.
- **WHY IT MATTERS:** Multi-dimensional reporting prevents one scalar error but does not yield a well-founded ordering or minimality result.
- **SEVERITY:** HIGH
- **REPAIR:** REQUIRED

### C14. Finite behavioural equivalence

- **CLAIM ATTACKED:** Matching all admissible queries over the frozen corpus is bounded evidence of non-unique factorisation.
- **FAILURE MODE:** The quantifier “all admissible c and q” is under-specified, while actual tests are finite. Behavioural equivalence can be accidental, overfit, or induced by a weak query algebra.
- **COUNTEREXAMPLE:** Representation A stores a field explicitly; B stores a code interpreted by a decoder, or a relation whose extension is exactly the frozen corpus. They agree on all tested cases and diverge on an untested value or composition.
- **WHY IT MATTERS:** Finite equivalence supports only indistinguishability under the tested contract, not semantic equivalence, necessity, or global non-uniqueness.
- **SEVERITY:** CRITICAL
- **REPAIR:** REQUIRED

### C15. Underdetermination of “minimal semantic basis”

- **CLAIM ATTACKED:** The contract can identify the smallest defensible factorisation without imposing an ontology.
- **FAILURE MODE:** Minimality is relative to corpus, obligations, representation language, decoder model, admissibility assumptions, and adjudication criteria. Different but coherent choices produce incomparable bases.
- **COUNTEREXAMPLE:** Treat a distinction as a generic relation, a typed attribute, or an explicit component; each can preserve the same observed answers with different accounting vectors.
- **WHY IT MATTERS:** The requested object is not uniquely determined by the observation contract.
- **SEVERITY:** CRITICAL
- **REPAIR:** REQUIRED

## D. Strongest successful attacks

1. **Contract-level ontology loading:** The challenge pairs and required properties repeatedly preselect identity continuity, normative versus technical status, epistemic support, external effect, uncertainty, temporal validity, and concurrency. Calling these “observed” does not make their decomposition neutral.
2. **Oracle leakage through adjudication:** Rules for opaque interpreters, generic carriers, hidden semantic force, “unrelated” observations, reliable evidence, and domain-specific relations require an evaluator to already know what counts as semantic force.
3. **Finite-equivalence overreach:** The methodology can establish only equality of answers for the tested query/corpus domain. It cannot establish globally different semantics or global non-minimality.
4. **Target-loaded holdouts:** Delaying generation until after freeze protects against direct memorization but not from a generator whose schema and transformations encode the same target distinctions.
5. **Architecture-loaded complexity:** A vector is better disclosure than a scalar, but without a common cost model it cannot rank heterogeneous representations.

## E. Failed attacks

- **Claim that every observation is necessarily ontology-loaded:** Not established. A formally specified, uninterpreted event log with externally fixed equality and order could be a useful neutral substrate. The current contract, however, does not fully provide that substrate.
- **Claim that two behaviourally equivalent representations cannot differ semantically:** Not established. The contract permits this possibility and supplies no representation-independent invariant that rules it out.
- **Claim that all generic relations are laundering:** Not established. A relation with a fixed, public, domain-neutral semantics can be legitimate structural machinery.
- **Claim that post-freeze holdouts are useless:** Not established. They can detect overfitting within a declared generator family, although they cannot by themselves establish target neutrality.
- **Claim that multi-vector complexity is meaningless:** Not established. It improves auditability and exposes trade-offs, but does not solve cross-formalism comparability.

## F. Hidden assumptions discovered

The instrument assumes, without a complete formal definition: what counts as an elementary record; identity and continuity criteria; event and observation individuation; the intended time/order model; the meaning of possible ordering; a compatibility theory for CONSISTENT; an intervention and external-effect model; reliability and verification semantics; the relationship between facts and reports; witness sufficiency; uniqueness under duplication; relevance under unrelated additions; admissible decoder power; the boundary between generic and domain-specific structure; a common model of payload and predicate cost; and a universe of admissible queries beyond the finite examples.

## G. Circularity / oracle leakage analysis

The contract denies a canonical ontology but reintroduces semantic commitments as obligations and adjudication tests. The evaluator decides whether a field is “catch-all”, whether a relation is doing domain-specific work, whether a source is reliable, whether a change is externally realized, and whether two records concern the same referent. Those decisions are semantic oracle functions. A participant may be prohibited from using an opaque interpreter while the evaluator is permitted an equally opaque interpretation of the contract.

This is not proof of intentional leakage; it is a structural leakage channel. The terms can be made operational only by fixing additional semantics, and fixing them narrows the claimed neutrality.

## H. Representation-independence analysis

The methodology supports implementation/formalism independence: two authors may choose different encodings and still be compared by common queries. It does not establish measurement-contract independence, because both authors inherit the same record vocabulary, pair construction, obligations, metamorphic predicates, and adjudication criteria.

Two representations with the same finite observable behaviour but different semantic factorisation are possible whenever the query set cannot distinguish explicit components from encoded relations, attributes, carriers, or decoder logic. This proves bounded observational indistinguishability under the declared contract and supports the possibility of non-unique factorisation over that domain. It does **not** prove that either factorisation is semantically equivalent globally, that either is minimal, that the hidden distinction is a legitimate semantic unit, or that the measurement contract is neutral.

No representation-independent invariant in the supplied methodology prevents this outcome. Bidirectional reconstruction helps, but the reconstruction mapping itself is judged using the same obligations and may conceal semantic interpretation.

## I. Holdout/metamorphic analysis

Post-freeze holdouts reduce direct overfitting to public pairs, but independence depends on the generator's sampling distribution and formal transformation semantics. A generator can be vocabulary-neutral yet distinction-loaded. Coverage of 25% is a quantity, not a guarantee of semantic diversity or adversarial strength.

Metamorphic tests are useful invariance probes only when the transformation preconditions and expected invariants are independently formalized. Otherwise “unrelated”, “witness”, “identical”, “irrelevant”, and “causal” are oracle terms. The tests also risk asymmetry: representations that expose structure make dependencies visible, while opaque encodings can conceal them.

## J. Complexity-accounting analysis

The vector is preferable to a scalar because it prevents incompatible costs from being silently collapsed. It remains architecture-loaded because vocabulary, constructor, decoder, relation, payload, exception, and assumption counts depend on the chosen formal language and accounting granularity. No normalization handles interpreter expressiveness, description length of rules, domain size, or semantic work hidden in generic machinery. Therefore the vector is an audit profile, not a valid objective function for minimality.

## K. Strongest possible valid conclusion

For a precisely declared finite corpus, query family, transformation family, and adjudication procedure, the experiment can provide bounded evidence about which representations are observationally distinguishable under that contract. It can reveal concrete reconstruction failures, expose some laundering strategies, and demonstrate that multiple encodings survive the tested obligations. It can report implementation-independent agreement and bounded non-uniqueness without claiming canonical semantics.

## L. Strongest conclusion that would be invalid

It would be invalid to conclude that the observation schema is ontology-free; that a surviving basis is globally or uniquely minimal; that matching holdouts establishes semantic independence; that a generic carrier/relation is semantically free; that a complexity vector ranks heterogeneous architectures; or that finite behavioural equivalence proves different internal factorisations in the world rather than indistinguishability under the selected queries.

## M. Required repairs, if necessary

Repairs are required for the stronger neutrality and minimality claims, not necessarily for a bounded comparison experiment:

1. Specify a participant-independent formal observation model with explicit granularity, identity, time, evidence, and uncertainty semantics, or narrow the claim to the model actually fixed.
2. Separate world facts, observations, reports, and adjudicator judgments with machine-checkable semantics; define reliability and witness rules.
3. Define MAY_ORDER, CONSISTENT, MUTATE, and “unrelated” formally, including concurrency versus ignorance.
4. Make holdout generation auditable, preregistered, and stress-tested by generators that do not share the same hand-selected distinctions.
5. Add adversarial cross-contract replications, not only independent encodings under one contract.
6. Treat relation, attribute, metadata, carrier, and decoder mechanisms with explicit semantic cost and inspectable mappings.
7. Use the complexity vector descriptively unless a formal partial order and cross-language cost model are supplied.
8. Restrict conclusions to finite, declared behavioural indistinguishability and label all extrapolation as unresolved.

## N. Whether another experiment is justified

YES, if the aim is to test neutrality or any claim beyond bounded observational comparison. The next experiment should vary the observation contract and holdout generator independently, include adversarially chosen alternative granularities and query semantics, and predeclare how disagreement is adjudicated. A repeat using only another representation language under the same contract is insufficient for the central neutrality claim.

## O. Explicit unresolved questions

1. What exact formal object is an elementary observation, and can its granularity vary without changing the result?
2. What makes two records concern the same continuing referent?
3. Is order temporal, causal, process, evidential, or a relation among these?
4. Does MAY_ORDER express concurrency, ignorance, or both?
5. What theory defines CONSISTENT?
6. What is the formal semantics of MUTATE and of externally realized effect?
7. Who determines source reliability and witness sufficiency?
8. How are duplicate observations distinguished from duplicate events?
9. How is “unrelated” established without a semantic oracle?
10. What is the admissible query universe, and how is “all” operationalized?
11. How are decoder power and opaque/generic relation power costed?
12. What evidence would count as measurement-contract independence rather than implementation independence?
13. Which conclusion, if any, is intended when two representations agree only on finite tests?
14. Can alternative observation contracts produce incompatible but equally defensible minimality results?

## P. Final verdict

The instrument is useful as a bounded, adversarial comparison protocol, but its stronger neutrality and minimality interpretation is not established. The principal blockers are ontology-bearing observation vocabulary, hidden identity/temporal/epistemic/normative assumptions, evaluator oracle leakage, target-loaded holdouts, architecture-loaded complexity accounting, and finite-equivalence overreach.

- Red Team: **FAIL**
- Measurement neutrality: **OPEN**
- Representation independence: **SUPPORTED** (implementation independence only; measurement-contract independence remains open)
- Global minimality implication: **UNSUPPORTED**
- Nothing omitted?: **NO**
- Remaining gaps: formal observation granularity; identity and continuity semantics; temporal/concurrency semantics; consistency theory; mutation/effect semantics; provenance/reliability rules; metamorphic preconditions; holdout-generator independence; cross-formalism cost model; admissible-query universe; and a principled adjudication rule for generic carriers and relations.
