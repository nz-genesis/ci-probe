# Semantic Basis Representation Contract V2

**Дата:** 2026-09-03  
**Статус:** `FROZEN MEASUREMENT INSTRUMENT / NOT CANONICAL`  
**Scope:** comparative semantic minimality under a bounded neutral discriminator corpus

## 1. Objective

Этот contract определяет, что считается admissible semantic basis element при сравнении конкурирующих factorisations. Он не определяет ontology Genesis.

Minimality is always relative to:

`declared corpus × declared obligations × representation contract × adjudication criteria`.

No result under this contract may be promoted to a globally minimal ontology claim.

## 2. Semantic basis element

A basis element is admissible only if all are true:

1. it has a stable semantic interpretation independent of implementation;
2. its semantic force can be inspected without executing an opaque interpreter;
3. it is independently variable in at least one discriminating case, or is required as a generic structural operator whose necessity is separately demonstrated;
4. it is composable with other elements;
5. removal produces either an observable reconstruction failure or forces another element to absorb independently variable semantic force;
6. its interpretation is bounded enough to permit adversarial comparison;
7. its semantic content is not defined merely as “whatever is needed to encode the rest”.

## 3. Composite-element rule

A named element is not treated as atomic merely because it has one label.

If an element contains two or more independently variable semantic coordinates, the evaluator must either:

- factor them into separately accountable components;
- demonstrate that their combination is itself the irreducible semantic unit;
- or classify the element as composite/bundled and exclude its raw element count from minimality comparison.

A record/tuple/object may contain multiple fields. Field count alone is not the metric; independently variable semantic force is.

## 4. Generic carrier rule

Ordinary carrier machinery such as:

- object/referent variables;
- equality/identity of variables;
- membership;
- ordinary set/sequence construction;
- generic composition;

is not automatically a domain-specific semantic primitive.

However, a semantic obligation cannot be declared “free carrier structure” if the carrier construction is doing domain-specific work that is necessary to distinguish cases.

## 5. Relation/attribute rule

Relations and attributes are not automatically free reductions.

When a proposed representation preserves a distinction through a relation, predicate, attribute, type or annotation, the evaluator must report:

- what semantic distinction it carries;
- whether that distinction is independently variable;
- whether the mechanism is generic or domain-specific;
- whether removing the mechanism destroys reconstruction;
- whether the mechanism is equivalent to a hidden primitive.

## 6. Removal criterion

For candidate element X:

`Remove(X) → Reconstruct(all obligations)`

is required for X to be reducible.

A successful reconstruction must preserve:

- semantic distinctions;
- temporal validity;
- causal/concurrency information;
- epistemic status;
- normative status;
- externally realized effects;
- identity continuity where required;
- uncertainty/failure distinction.

A prose assertion that reconstruction is possible is insufficient; a concrete mapping or counterexample is required.

## 7. Merge criterion

For X and Y, merge is admissible only if:

1. every discriminating case remains distinguishable;
2. independently variable semantic coordinates remain explicitly recoverable;
3. no opaque payload or unrestricted predicate carries hidden semantic force;
4. the merged element does not become a catch-all bucket whose interpretation changes per case;
5. the merged representation does not rely on target vocabulary unavailable to a clean-room evaluator.

## 8. Split criterion

Splitting a named element is justified only when its components have independently variable semantic force and at least one discriminating case changes one while holding the other materially fixed.

Naming convenience is not evidence of semantic independence.

## 9. Structural-layer criterion

Temporal, causal, concurrency and carrier structure may be represented by generic relations rather than counted as domain-specific primitives.

But the evaluator must prove that:

- the generic relation mechanism is sufficient;
- no domain-specific semantic meaning is hidden in it;
- the relation does not collapse distinct temporal, causal or concurrency obligations;
- removing it can be reconstructed from remaining structure if it is claimed reducible.

## 10. External-effect criterion

An attempted action and an externally realized effect must remain distinguishable whenever the corpus contains a case where they diverge.

Recording an attempt is not evidence that the external world changed.

## 11. Epistemic criterion

The representation must preserve at least these distinctions where present in the corpus:

- external fact;
- observation/report;
- evidential support/provenance;
- unresolved/unknown result;
- confirmed success/failure.

These may be factorized differently, but cannot be collapsed merely by using a broad “claim” or “status” field.

## 12. Normative/technical criterion

The representation must preserve technical possibility/enabling conditions separately from normative permission/legitimacy wherever the corpus contains their independent variation.

A generic “constraint” bucket is not accepted as an automatic reduction unless its internal semantic structure is shown and remains admissible under the composite-element rule.

## 13. Identity criterion

The representation must preserve continuity of a referent across time and distinguish it from coincidentally identical observable conditions.

Whether this requires a Genesis primitive is an empirical adjudication question. Ordinary carrier identity/equality may satisfy the obligation if it does not hide additional domain-specific semantics.

## 14. Equivalence

Two bases are semantically equivalent over the declared corpus only if there are bidirectional reconstruction mappings preserving every declared obligation and all required counterexamples.

Equivalence is relative, not global.

## 15. Anti-trivialization

The following are disallowed as reductions:

- arbitrary JSON/object encoding;
- unrestricted “metadata” fields;
- catch-all predicates;
- target-vocabulary leakage;
- interpreter-defined opaque tokens;
- prose conventions carrying unaccounted semantic force;
- changing the corpus after seeing a candidate answer;
- counting a bundle as one solely because it has one name.

## 16. Adjudication outputs

Each candidate must receive separate labels for:

- coverage;
- atomicity;
- removal behavior;
- merge behavior;
- split behavior;
- anti-laundering;
- temporal/concurrency preservation;
- epistemic preservation;
- normative preservation;
- external-effect preservation;
- implementation independence;
- corpus generalization risk.

No single scalar score may replace these dimensions.

## 17. Closure rule

Semantic closure requires all material discriminating cases to have one of:

`PASS`, `FALSIFIED`, or `EXPLICITLY UNRESOLVED WITH BOUNDED REASON`.

“Looks minimal” is not an admissible closure state.

## 18. Freeze decision

Red Team completed 2026-09-03. Conceptual blockers were addressed by separating evaluator metadata from participant-facing content, requiring composite-element accounting, and explicitly testing carrier/identity and structural-layer boundaries.

The contract is frozen as a measurement instrument for the declared bounded corpus. It remains non-canonical and cannot establish global ontology minimality.
