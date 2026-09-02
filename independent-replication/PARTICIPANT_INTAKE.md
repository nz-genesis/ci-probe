# Clean-Room Participant Intake

This file defines how a materially independent participant can contribute a replication without giving the public repository or Genesis Lab an opportunity to steer the result.

## 1. Before starting

Use the frozen IR-V2 challenge and record:

- challenge revision/commit;
- challenge SHA-256: `03b25456a1ad0b40272daa1ca633910855433cfdce6ece8d0cf9e3352cd7ef1b`;
- participant type: independent human/team, separate model/provider, independently governed solver/agent, or equivalent;
- tools and model/provider, if any;
- date/time and timezone;
- whether any Genesis private material, target basis, reduction map, adjudication, or Genesis-specific semantic labels were visible.

Do not inspect private Genesis research before the commitment is frozen.

## 2. Produce the raw result

Create the result independently from the challenge. Preserve the raw bytes unchanged.

The result must contain the IR-V2 submission fields:

- `basis`
- `case_mappings`
- `deletion_analysis`
- `counterexamples`
- `uncertainty`
- `provenance`
- `candidate_visibility`

Also record `challenge_sha256` and may include additional fields for omitted obligations, challenge criticism, or alternative models. The challenge is bounded; discovering that it is incomplete is a valid result.

## 3. Commit before comparison

Compute the commitment using the public commit-reveal verifier and publish only the commitment first.

Do not publish the secret nonce or raw result at this stage.

The commitment must bind both the exact challenge and exact raw submission. Preserve the original raw bytes and nonce locally until reveal.

## 4. Public record

Open or comment on the active recruitment issue with:

- participant identifier chosen for the study;
- participant type;
- challenge revision and SHA-256;
- commitment;
- tool/model provenance at a level that does not reveal secrets;
- candidate-visibility statement.

Do not put the raw result, nonce, private Genesis material, credentials, or unpublished datasets in the pre-reveal record.

## 5. Reveal

After the agreed comparison window, publish the raw submission and nonce. Run the public verifier against the exact frozen challenge and preserve its output.

A verifier PASS establishes integrity and structural contract compliance only. It does not establish semantic correctness.

## 6. Independence adjudication

Genesis must classify the evidence path independently from semantic agreement:

- `MATERIAL_INDEPENDENCE_CONFIRMED`
- `PARTIAL_INDEPENDENCE`
- `NOT_INDEPENDENT`
- `UNDETERMINED`

A different account, prompt, persona, or model wrapper alone is not sufficient if the epistemic source remains materially shared.

## 7. Comparison and Red Team

Only after reveal may the result be compared with Genesis hypotheses or other submissions. Preserve the raw result unchanged and record separately:

- agreements;
- disagreements;
- novel distinctions;
- omitted obligations/domains;
- strongest counterexamples;
- unresolved uncertainty;
- Red Team findings.

A disagreement is a valid research outcome and must not be scored as a failure merely because it differs from Genesis.

## 8. Evidence boundary

This process is an independent evidence-acquisition mechanism. It does not authorize a participant to access private Genesis state, and it does not by itself change Genesis canonical architecture or ontology.
