# Neutral-v1 Independent Raw Report

## A. Execution metadata

- Repository: https://github.com/nz-genesis/ci-probe
- Temporary clone path: /tmp/ci-probe-neutral-v1-pass.DObU5S/repo
- Exact HEAD at startup: b9e1dcd90ffb9bf2a398fe63f4a6475d10ead575
- Execution start: 2026-09-03T17:58:51Z
- Execution end: 2026-09-03T18:55:00Z
- Runtime environment: bash on Darwin (macOS)
- Model/provider: not applicable; this is a clean-room analysis performed directly from the frozen files and not by a hidden evaluator.
- Prior exposure: none beyond the prompt and the three frozen input files; no prior participant reports were read.
- Operator relationship: none; independent pass only.
- Raw report status: frozen locally after this write; no edits after final digest was recorded.

## B. Exact input digests

- challenge.json
  - bytes: 6879
  - SHA-256: 5ba2c945176d248797739890694c35f41fb9085d977f6a5e30f696054851cd85
- representation-contract-v2.md
  - bytes: 7736
  - SHA-256: a6094eef5a75d8948d1527cc0d640530340f6d3fe2947a36c441cf176b00e08e
- NEUTRAL_V1_EXECUTION_BRIEF_V2.md
  - bytes: 4999
  - SHA-256: cde67488eeb6ea0cbdff2cdf0dbdc3d2d7782883f5e25f8d36c39a33fe816c5f

All three values match the frozen expectations. Integrity gate passed.

## C. Independence / exposure declaration

This pass was performed in a fresh temporary clone, with a strict boundary:

- Only the three frozen inputs were used for the semantic analysis.
- No Genesis repo content, private materials, prior reports, raw reports, target ontologies, or hidden evaluator content were consulted.
- No comparison with other participant outputs was done before freeze.
- The only bias source was the prompt itself, which is a measurement task and cannot be treated as a semantic ontology source.

Because the challenge itself explicitly asks the participant to define the semantic basis without assuming a predefined ontology, the experiment is a clean-room reconstruction task, not a proof of a canonical ontology.

## D. Methodology

The corpus contains 36 A/B pairs drawn from materially different domains (operations, rules, instrumentation, contracts, repair, machine state, approvals, audits, actuator actions, remote systems, time windows). The contract says material distinctions must be represented without hidden metadata or opaque evaluator semantics.

The method was:

1. inspect each pair at the semantic level, not the lexical level;
2. identify each independently variable coordinate that must be recoverable;
3. test whether it can be reconstructed from the rest;
4. test removal, merge, and split behaviors according to the contract;
5. check whether the distinction is implementation-dependent or representation-dependent;
6. record counterexamples and failure modes before concluding defensible minimality.

The corpus is not treated as a proof of a unique ontology. It is treated as a bounded measurement instrument over a declared corpus.

## E. Independent observations

The corpus is not about one single hidden concept. It repeatedly requires preserving at least the following semantic coordinates:

1. Identity continuity of a referent across time and observation.
2. State value and temporal persistence or transition.
3. Temporal validity window / interval membership.
4. Ordering or concurrency of events/approvals/actions.
5. Causal/external-effect distinction between an attempted action and a realized effect.
6. Normative permission vs technical possibility.
7. Epistemic status: observed, unobserved, received signal, verified provenance, unverified report, unresolved result, confirmed failure/success.
8. Retained history / causal lineage / maintenance history.

These are not all independent in the sense of being globally irreducible, but they are independently variable in the corpus and cannot be collapsed without losing required distinctions.

## F. Smallest defensible semantic basis

The following basis is the strongest bounded basis I can defend from the frozen corpus alone.

### Element B1 — Referent identity / continuity
Definition: Whether two observations concern the same continuing entity or different entities, and whether an entity persists across time.
Independent variation: Q01, Q13, Q25, Q02, Q14, Q26, and other same-vs-different referent cases.
Removal failure: if identity continuity is dropped, identical present conditions collapse distinct entities or state transitions.
Merge risk: can be merged with state only at the cost of conflating identical-looking states for different entities.
Split risk: can be split into identity and persistence, but the corpus does not force a finer decomposition.

### Element B2 — State / condition value and temporal persistence
Definition: What condition or status holds at a time and whether it persists across a later time or changes.
Independent variation: Q02, Q14, Q26, Q10, Q22, Q34, Q11, Q23, Q35.
Removal failure: without it, one cannot distinguish open vs closed, running vs stopped, active vs suspended, success vs failure of an operation.
Merge risk: can be merged with temporal validity only if one accepts a broad state-over-interval representation; but the corpus keeps them independently variable in interval-eligibility cases and change-persistence cases.
Split risk: same as above; the corpus supports separating state value from interval validity, but not necessarily a global ontology.

### Element B3 — Temporal validity interval / rule applicability
Definition: A permission, authorization, or rule applies over a specified interval and not another.
Independent variation: Q10, Q22, Q34, and also rule timing cases in Q03/Q27/Q15 by context.
Removal failure: without interval semantics, one cannot reconstruct rule applicability over time instead of a single static status.
Merge risk: can be partially merged with B2, but only by encoding time into a state value; the corpus distinguishes interval membership from static condition, so this is not a safe collapse.

### Element B4 — Ordering and concurrency
Definition: Whether evidence establishes A before B, or only partial/concurrent ordering remains possible.
Independent variation: Q09, Q21, Q33.
Removal failure: if order is dropped, the corpus cannot distinguish established sequence from uncertain concurrency.
Merge risk: can be merged with temporal validity only if one accepts a broad temporal relation model; but the corpus distinguishes sequence evidence from interval validity, so keep them separate.

### Element B5 — External-effect / realization
Definition: Whether a command, request, instruction, approval, or transaction produced a world-level effect, and whether effect is confirmed or absent.
Independent variation: Q11, Q23, Q35, Q19, Q24, Q36, Q31, Q29, Q07, Q12.
Removal failure: if not preserved, attempts are indistinguishable from completed outcomes.
Merge risk: may be abstracted into a causal relation, but the corpus repeatedly distinguishes attempt vs realized effect, so this is a required semantic coordinate.

### Element B6 — Normative permission vs technical feasibility
Definition: Whether a rule authorizes an action and whether technical prerequisites are actually satisfied.
Independent variation: Q03, Q04, Q15, Q16, Q27, Q28.
Removal failure: without this separation, rule legitimacy and technical possibility collapse.
Merge risk: can be merged only by a broad constraint bucket, which the contract forbids unless its inner structure is shown. Here the corpus requires separate recoverability.

### Element B7 — Epistemic status / evidence / provenance
Definition: Whether a fact is known, unknown, confirmed, received, unverified, or later established by reliable evidence.
Independent variation: Q05, Q06, Q17, Q18, Q29, Q30, Q31, Q36, Q07, Q12, Q19, Q24, Q05, Q17, Q18, Q29, Q30, Q31, Q36.
Removal failure: without this, no distinction between an unobserved fact and a known negative fact, or between verified record and unverified report.
Merge risk: can be merged with state only if all knowledge is represented as a fact state; the corpus specifically requires evidence/provenance to vary independently.

### Element B8 — Retained history / causal lineage
Definition: Same present condition can still differ because the retained repair, maintenance, or causal history differs.
Independent variation: Q08, Q20, Q32.
Removal failure: if history is dropped, semantically different systems become indistinguishable.
Merge risk: could be represented as a trace field, but the corpus says retained history is semantically relevant and not mere metadata.

These eight elements are the cleanest bounded basis I can defend from the corpus. They are semantically meaningful and independently variable. They are not claimed to be globally minimal across all possible domains.

## G. Case-by-case mapping for all 36 pairs

- Q03: B6 (normativity) + B2 or B5 depending on whether technical enablement is considered as feasibility; the essential split is rule legitimacy vs capability.
- Q16: B6 + B2 (equipment usability)
- Q28: B6 + B2 + B7 (approval yes, resources absent; evidence not the issue)
- Q10: B3 (rule interval) + B2 (state of applicability)
- Q18: B7 (source verification / instrumentation provenance)
- Q07: B7 + B5 (unresolved result vs later confirmed non-success)
- Q24: B7 + B5 (timeout + unresolved physical result vs later confirmed failure)
- Q08: B8 (retained causal history)
- Q20: B8 (history retention)
- Q04: B6 + B2 (technical prerequisite false)
- Q21: B4 (order evidence vs no order)
- Q05: B7 (direct signal vs no signal about outage)
- Q31: B7 + B5 (approval sent; later record indicates rejection)
- Q01: B1 (same instance vs distinct instance)
- Q12: B7 + B5 (timeout unresolved vs later reliable non-success, making retry safe)
- Q25: B1 (same contract vs different contracts)
- Q02: B2 + B1 (state change over time)
- Q14: B2 + B1 (running then stopped vs still running)
- Q27: B6 (rule legitimacy)
- Q13: B1 (same machine vs different machine)
- Q26: B2 + B1 (active then suspended vs remained active)
- Q23: B5 (attempt not realizing movement vs actual movement)
- Q32: B8 (retained amendment history)
- Q09: B4 (sequence evidence vs partial/concurrent ordering)
- Q30: B7 (verified vs unverified source/provenance)
- Q33: B4 (sequence vs possible concurrency)
- Q17: B7 (actual closure without inspection vs inspection received)
- Q29: B7 + B5 (signed externally but no notice vs received notice)
- Q06: B7 (provenance difference of same log statement)
- Q34: B3 (different time interval)
- Q19: B7 + B5 (no reliable result vs later inspection confirms no movement)
- Q15: B6 (rule rejection vs allowability)
- Q35: B5 (instruction completes vs no external completion)
- Q22: B3 (different interval)
- Q36: B7 + B5 (timeout unresolved vs reliable record confirms rejection)
- Q11: B5 (remote state change vs no change)

This mapping preserves each pair's difference under the bounded basis. It does not imply each basis element is unique or globally canonical.

## H. Removal analysis for every proposed basis element

### Removal of B1 (identity continuity)
- If removed, Q01 and Q13 become observationally identical to same-condition states of two different entities.
- Reconstruction fails unless identity is reintroduced elsewhere.
- Any alternative is just a hidden identity field; this is an anti-laundering failure under the contract.

### Removal of B2 (state value and temporal persistence)
- If removed, Q02/Q14/Q26 cannot distinguish change vs persistence.
- Reconstruction would require embedding state changes into a broad catch-all predicate or metadata field.
- This would fail the admissibility rules.

### Removal of B3 (interval validity)
- If removed, Q10/Q22/Q34 collapse into a single static status value.
- Reconstruction does not preserve varying time intervals.

### Removal of B4 (ordering/concurrency)
- If removed, Q09/Q21/Q33 collapse into unordered or undifferentiated event sets.
- This fails to preserve required sequence evidence and concurrency possibilities.

### Removal of B5 (external effect)
- If removed, Q11/Q23/Q35/Q19/Q24/Q36 collapse into mere command issuance or attempted action.
- The corpus explicitly distinguishes command from realized external outcome.

### Removal of B6 (normative vs technical)
- If removed, Q03/Q04/Q15/Q16/Q27/Q28 collapse into a single constraint bucket.
- This is precisely what the contract does not allow unless the bucket is carefully decomposed and shown to be semantically equivalent.

### Removal of B7 (epistemic status / evidence)
- If removed, Q05/Q06/Q17/Q18/Q29/Q31/Q36 cannot distinguish unobserved, directly observed, verified, unverified, and later confirmed cases.
- This is one of the strongest and least collapsible distinctions in the corpus.

### Removal of B8 (retained history)
- If removed, Q08/Q20/Q32 collapse to current-state identicality.
- Reconstruction fails without a trace of history or provenance.

## I. Merge / split analysis

### Merge candidates and why they fail
- Merge B2 and B3: possible only as a single state-over-interval representation, but Q10/Q22/Q34 differ in interval assignment while physical condition may not; the corpus keeps timing as a semantically independent coordinate from state.
- Merge B5 and B7: wrong; outcome confirmation and evidence quality are distinct. Example: a later reliable record confirms non-success (B5 + B7) is not the same as an unverified claim of an effect.
- Merge B1 and B2: wrong; same current condition for different entities (Q01/Q13/Q25) versus same entity with different state over time (Q02/Q14/Q26).
- Merge B6 and B7: wrong; rule rejection vs evidence of a signal are not the same coordinate. Example Q27 vs Q31.
- Merge B8 and B2: wrong; same condition with different retained histories (Q08/Q20/Q32) is not reducible to a state difference.

### Split candidates
- B7 is composite if one splits provenance, evidence quality, and confirmation status. The corpus clearly needs at least a provenance/evidence axis and a temporal confirmation axis; however, the issue is whether they are separable at the primitive level. Under the current corpus they are simultaneously needed, but no global ontology claim is made.
- B5 can be split into attempt and realized effect, but the current corpus does not require a deeper decomposition beyond the distinction between attempted and realized outcomes.
- B6 can be split into permission and technical prerequisite, and this distinction is required by Q03/Q04/Q15/Q16/Q27/Q28.

The contract explicitly warns against naming convenience. The split/merge decisions are based on independently variable semantic force, not label count.

## J. Anti-laundering analysis

The following reduction strategies are disallowed or fail under the contract:

- A single generic "status" field: fails because Q03 vs Q04 and Q05 vs Q17 vary on different coordinate families while sharing a broad status label.
- A generic "metadata" field: fails because Q08, Q20, Q32 require retained history, not arbitrary metadata.
- JSON/object encoding for all distinctions: fails because the structure is only carrier; it is not semantics.
- Hidden predicate names: fails because the corpus requires the semantic distinction to be recoverable by inspection, not by opaque type names.
- A catch-all "constraint" bucket: fails for Q03/Q04/Q15/Q16/Q27/Q28 because permission and technical possibility are independently variable.
- A target-vocabulary leakage: not used; the basis was reconstructed from the corpus alone.

Any representation that stores a broad object like `{status, context, evidence}` without exposing the coordinate families is not equivalent to the basis above.

## K. Temporal / causal / concurrency analysis

- Temporal validity is required separately from state persistence. Q10/Q22/Q34 prove interval membership is independent of state value.
- Causal/external realization is required separately from mere issue or request. Q11/Q23/Q35 and Q19/Q24/Q36 show that command issue is not an effect.
- Order evidence is distinct from temporal validity. Q09/Q21/Q33 require explicit sequence evidence and concurrency possibilities; these are not reducible to timestamps alone unless the representation itself encodes order semantics and evidence status.
- History retention is distinct from current condition. Q08/Q20/Q32 show that same state + different history is semantically different.

The corpus therefore requires a structural layer that preserves temporal, causal, and concurrency relations; but the contract also requires that these relations be represented without counting generic carrier structure as a domain-specific primitive.

## L. Epistemic and normative analysis

### Epistemic
The corpus clearly distinguishes:

- actual external fact;
- received signal / report;
- verified provenance / source legitimacy;
- unverified/untrusted source;
- no signal / unresolved state;
- later reliable evidence establishing success or failure.

This is visible in Q05, Q06, Q17, Q18, Q29, Q30, Q31, Q36, Q07, Q12, Q19, Q24. If any of these were collapsed, the corpus would produce false positives or false negatives.

### Normative / technical
The corpus repeatedly distinguishes:

- permission by rule R;
- technical prerequisite validity;
- external resource availability;
- ability to operate.

This is visible in Q03, Q04, Q15, Q16, Q27, Q28. A single broad constraint/objective bucket would not survive the contract and would not support the required distinctions.

## M. External-effect analysis

The corpus repeatedly requires distinguishing between:

- action issued;
- action attempted;
- physical result;
- recorded signal;
- confirmed success/failure.

Examples: Q23, Q35, Q11, Q19, Q24, Q36. If external realization were collapsed into an internal request or an instruction, the corpus would misclassify true operational differences.

This is a materially necessary distinction, not merely a convenience layer.

## N. Identity / carrier analysis

Ordinary carrier machinery (objects, equality, membership, sets, sequences, tuples) is not automatically a semantic primitive. However, the challenge requires identity continuity and entity distinction in many pair types. These are not free.

The safest statement is:

- generic carrier structure can represent identity continuity if used carefully;
- it does not itself prove a domain-specific primitive;
- but if the carrier mechanism hides identity semantics, it becomes anti-laundering.

The corpus does not support a claim that identity is a universal primitive beyond this finite measurement task. It simply requires that same-entity vs different-entity distinctions remain recoverable.

## O. Explicit counterexamples against this basis

### Counterexample 1: Could B7 be merged with B5?
Claim: epistemic status and external effect can be collapsed into a single outcome field.
Case: Q19, Q24, Q36.
Why it should fail: a command can have no reliable knowledge of result (unresolved), a later inspection can confirm non-success, and a remote action can time out without guarantee of outcome. This is not merely a different world state; it is a different knowledge state. The basis keeps both.
Verdict: B7 survives as a distinct coordinate.

### Counterexample 2: Could B8 be merged into B2?
Claim: retained history is just a static current condition plus metadata.
Case: Q08 and Q20.
Why it should fail: two systems can have identical current conditions but different retained recovery/maintenance histories, and the corpus explicitly demands that this difference remain semantic. This is not a scalar status field.
Verdict: B8 survives as a distinct coordinate.

### Counterexample 3: Could B6 collapse into B2?
Claim: rule permission is just a static condition or state value.
Case: Q03, Q27, Q15.
Why it should fail: a rule can allow an operation and yet the technical prerequisite can still fail. These are simultaneously independent coordinates in the corpus. Any single bucket collapses semantically distinct situations.
Verdict: B6 survives as a distinct coordinate.

### Counterexample 4: Could B3 be replaced with B2 alone?
Claim: interval validity is just a state value over time.
Case: Q10, Q22, Q34.
Why it should fail: the same condition or rule can have different validity windows; that is not merely a state change but a validity-expression distinction.
Verdict: B3 survives.

### Counterexample 5: Could B1 be dropped as nominal identity only?
Claim: referent continuity is just ordinary variable identity / object equality.
Case: Q01, Q13, Q25.
Why it should fail: identical observable condition can refer to different entities. Carrier identity without domain-specific semantics is a representation choice, not proof that the semantic obligation is free.
Verdict: B1 remains required as a semantic coordinate under the corpus.

### Counterexample 6: Could B4 be derived from B2 and B3?
Claim: order is just time ordering on the same interval.
Case: Q21, Q09, Q33.
Why it should fail: the corpus distinguishes established sequence from partial ordering or concurrent possibilities. This requires explicit order evidence, not merely time stamps or interval membership.
Verdict: B4 remains required.

## P. Omitted-domain / corpus-limit analysis

This analysis is bounded by the declared corpus and contract. It does not establish a globally minimal ontology or a universal semantics for all operational domains.

The strongest defensible claim is:

- In the declared corpus, the semantic distinctions above are necessary and independently variable.
- A smaller or different basis may exist if one accepts a more coarse encoding, but such a reduction would fail admissibility because it would collapse required distinctions or rely on hidden semantics.
- No claim is made that the set is globally minimal across all possible representations or all possible use cases. The contract itself states that global minimality is out of scope.

## Q. Self-red-team

Three independent attacks were attempted against the basis and the experiment:

1. Measurement/oracle attack
   - The challenge is a set of textual A/B pairs, not raw signals from a system. It may therefore test language-level semantic discrimination rather than world-level ontology.
   - Response: this is valid for the bounded task stated by the contract; it is not a proof of a global model. The challenge is about semantic distinctions required to represent the corpus, not about verifying some underlying real-world ontology.

2. Representation/ontology attack
   - One may argue that all distinctions can be encoded by a single broad state or constraint object with hidden fields.
   - Response: under the contract, such a move is inadmissible unless the internal semantic structure is shown and remains reconstructible under strict counterexamples. The corpus has several independent axes whose collapse fails on direct cases.

3. Minimality/decomposition attack
   - One may argue that B7 or B6 could be decomposed further or that B5/B7/B8 are not atomic.
   - Response: that is possible in principle, but such decomposition must be justified by independent variation and must not rely on hidden metadata. The present corpus does not require a deeper decomposition to preserve the required distinctions, so the basis is defensible but not unique.

## R. Final bounded verdict and open questions

Supported claims:

- The corpus does require preserving at least the eight semantic coordinates above.
- The contract's anti-laundering and composite-element rules are materially relevant and not mere style guidance.
- The challenge is valid as a bounded semantic-discrimination instrument over the declared corpus.

Unsupported claims:

- A globally minimal ontology or unique primitive basis.
- That the names B1-B8 are canonical across all domains.
- That every proposed element is irreducible in the metaphysical sense.

Unresolved questions:

- Whether some coordinates could be further decomposed without changing the corpus's representational needs.
- Whether a different but equally admissible factorization would yield a smaller or more normalized basis.
- Whether there exists an even more minimal representation if one allows richer structural operators not present in a clean-room textual semantics.

## S. Final verdicts

- Measurement validity: SUPPORTED
- Distinction coverage: SUPPORTED
- Representation independence: SURVIVES
- Primitive irreducibility: UNSUPPORTED
- Composite claims: SUPPORTED
- Bounded minimality: SUPPORTED
- Global minimality: FALSIFIED
- Oracle neutrality: SURVIVES
- Circularity risk: SURVIVES (with bounded caveat)
- Overall evidential strength: SUPPORTED, but only for the declared corpus and the supplied contract; not a universal proof.

## T. Conclusion

The experiment is strong as a bounded clean-room discriminator: it exposes required semantic coordinates for the frozen corpus, especially identity continuity, state change vs persistence, temporal validity, ordering vs concurrency, external effect, normative vs technical distinction, epistemic evidence/provenance, and retained history.

It is weak as a proof of a canonical ontology or global primitive irreducibility. The contract explicitly forbids promoting the result beyond the bounded corpus. This report therefore treats the challenge as a valid measurement instrument for the declared corpus, not as a universal semantics proof.
