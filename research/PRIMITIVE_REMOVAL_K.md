# Primitive Removal K — Seven-Dimension Counterfactual

## Question

Does the current seven-dimension working basis prove that each named dimension must be a Genesis primitive, or only that each distinction can matter semantically?

## Method

For each of:

```text
State
Transition
Capability
Authority
Observation
Evidence
Constraint
```

construct a pair of records differing only in that dimension.

1. Project the pair while omitting the dimension.
2. Confirm that the projection collides, establishing that the distinction is semantically relevant to that fixture.
3. Re-encode the omitted value as generic attributed data rather than as a dedicated primitive.
4. Confirm that the distinction remains recoverable.

## Result

All seven fixtures collide under naive omission, but all seven remain distinguishable under the same uniform generic attributed-data representation.

Therefore the experiment establishes:

```text
semantic distinction may be necessary
≠
named primitive is necessary
```

The experiment does **not** establish that all seven can be safely eliminated from a complete Genesis ontology. Generic attributed data can preserve information while losing domain-specific invariants, authority boundaries, validation guarantees, or compositional affordances.

## Red Team

- **Semantic laundering:** the generic representation intentionally carries the dimension as data; this is a representation test, not proof that the dimension has no semantics.
- **Invariant laundering:** no claim is made that arbitrary metadata preserves all invariants. This remains open.
- **Domain closure:** only seven synthetic one-dimension fixtures are used; heterogeneous Genesis tasks are not closed.
- **Information vs ontology:** collision proves information loss under projection, not primitive irreducibility.
- **Executable validity:** the public workflow is the authoritative executable check; local execution alone is insufficient.

## Epistemic status

`OBSERVED / BOUNDED`

## Conclusion

No new primitive is justified by this experiment. More importantly, the current seven-element candidate basis must not be mistaken for seven proven irreducible primitives merely because each dimension can distinguish a pair of cases.

The next reduction question is invariant preservation: whether removing a named dimension while retaining the remaining semantics can preserve the *specific guarantees* attached to that dimension across heterogeneous cases.
