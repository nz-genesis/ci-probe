# P207 Public Contract Boundary

`ci-probe` is a public Genesis-agnostic control repository.

It may validate the shape and non-disclosing properties of a P207 witness exported from private `genesis-lab`. It must never receive raw private Genesis state, private corpus, canonical Genesis decisions, or private semantic-authority payloads.

A public `PASS` means only that the supplied record satisfies the public contract. It does not prove that private Genesis semantics were preserved.

The private correspondence result, evidence interpretation, genealogy, and canonical decision belong to private `genesis-lab`.
