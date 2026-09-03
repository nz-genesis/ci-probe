# Neutral Semantic Basis Challenge V1

Participant-facing clean-room package for an independent semantic-basis reconstruction.

## Frozen input revision

Use the exact Git commit:

`d58e7e61ecb173ab7e2b88c53c9438f6e2c34077`

Do not substitute another commit or branch head.

## Allowed semantic inputs

Read only these two files:

- `independent-replication/neutral-v1/challenge.json`
- `independent-replication/neutral-v1/representation-contract-v2.md`

Do not inspect other repository files, Git history, prior experiment artifacts, or external Genesis materials.

## Integrity

The frozen challenge file is 6879 bytes. Before semantic work, compute the SHA-256 of the exact checked-out bytes and record the actual value in the raw report.

The representation contract is the frozen canonical contract content used to build this package. Do not substitute another copy. Compute and record its actual SHA-256 locally before semantic work.

The package README intentionally does not publish a guessed or stale digest for the contract. The local computed digest is the authoritative execution-time check for this exact commit.

## Clean-room execution

Prefer a shallow clone or otherwise obtain only the exact frozen commit so repository history cannot influence the analysis. Do not use repository search or history browsing to discover prior Genesis results.

If any supplied input is missing, mutated, or otherwise inconsistent, abort before semantic reasoning and report the exact failure.

## Important epistemic boundary

This package is a bounded measurement instrument. A successful result may support conclusions only for the declared corpus, obligations, representation contract, and adjudication criteria. It does not by itself establish globally minimal Genesis ontology.
