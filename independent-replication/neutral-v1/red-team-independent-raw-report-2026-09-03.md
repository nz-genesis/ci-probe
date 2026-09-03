# Neutral V1 Independent Raw Red-Team Report

## A. Execution metadata
- Execution date: 2026-09-03 (start 2026-09-03T21:48:14+03:00; end recorded at freeze below).
- Source: `https://github.com/nz-genesis/ci-probe.git`, commit `c8eece974aeb9acb719393ea74b302dcc24aefb0` (main/HEAD at clone).
- Clean-room clone: fresh clone performed before analysis; no repository files other than the three authorized inputs were inspected.
- Model/provider/runtime: GitHub Copilot CLI, API session runtime (exact model/version not exposed by runtime).
- Relationship to corpus owner/operator: independent evaluator; no relationship or coordination known.
- Prior exposure: none declared. I had no prior participant result, candidate ontology, private material, evaluator label, or target vocabulary. Only the three frozen inputs below were used.

## B. Integrity gate and exact input digests
Integrity gate passed before semantic analysis: all expected paths existed at the cloned commit and bytes were hashed.

| input | bytes | SHA-256 |
|---|---:|---|
| `independent-replication/neutral-v1/challenge.json` | 6879 | `5ba2c945176d248797739890694c35f41fb9085d977f6a5e30f696054851cd85` |
| `independent-replication/neutral-v1/representation-contract-v2.md` | 7736 | `a6094eef5a75d8948d1527cc0d640530340f6d3fe2947a36c441cf176b00e08e` |
| `independent-replication/NEUTRAL_V1_EXECUTION_BRIEF_V2.md` | 4999 | `cde67488eeb6ea0cbdff2cdf0dbdc3d2d7782883f5e25f8d36c39a33fe816c5f` |

Prompt-contract SHA-256 (the representation contract used as the prompt constraint): `a6094eef5a75d8948d1527cc0d640530340f6d3fe2947a36c441cf176b00e08e`.

## C. Independent semantic basis
The smallest defensible factorisation I can support over this corpus is the following. Names are descriptive, not claims about a universal ontology.

1. **Referent/identity continuity (I):** which entity, service instance, contract, machine, document, or transaction a statement/action concerns, including continuity across time and distinction of coincident conditions.
2. **Observable/current state (S):** a condition or state value of the referent (open/closed, running/stopped, active/suspended, movement/no movement, availability, success/non-success).
3. **Action/attempt and external effect (A/E):** an issued/intended operation or attempt, separately from whether the external world realized its effect. The separation is mandatory where attempts time out or commands do not move/change state.
4. **Normative permission (N):** allowed/rejected/legitimate under a rule or authorization.
5. **Technical enablement (T):** executable/performable prerequisites and resource/equipment availability.
6. **Temporal validity (V):** interval or time scope during which a rule/approval/authorization applies.
7. **Temporal/causal ordering (O):** established precedence versus partial/concurrent ordering; this is relation structure, but carries independently variable semantics.
8. **Epistemic status (K):** external fact versus observation/report/record, receipt/notice, verification/provenance, and support status. Provenance/verification is not truth and receipt is not external occurrence.
9. **Outcome uncertainty/finality (U):** unresolved/unknown result versus reliably confirmed success or non-success/rejection. This is not reducible to state or epistemic source.
10. **Retained history (H):** materially different retained causal/maintenance/amendment history despite equal present state. History may be represented as a structured record, but its independently variable content cannot be silently discarded.

`A/E`, `K`, and `U` are deliberately not bundled: an attempt can be known while its effect is unknown; an effect can be false while the attempt is known; a report can be verified without being the external fact. `I` and `S` are also separate: identical observations may concern different referents.

## D. Case-by-case mapping (all 36)
Notation: each entry identifies the coordinate(s) that differ between A and B and the adversarial reason it cannot be inferred from the others.

- **Q01 — I:** same condition/times, distinct service instances versus one continuing instance. State and times are held fixed; identity continuity is independent.
- **Q02 — S:** open then closed versus open then still open. Same referent and observations; transition/state differs.
- **Q03 — N:** executable operation allowed versus rejected. Technical enablement held fixed; permission differs.
- **Q04 — T:** allowed operation with prerequisites versus one missing prerequisite. Normative permission held fixed; technical enablement differs.
- **Q05 — K:** actual outage with no received signal versus actual outage with direct signal received. External fact held fixed; receipt/epistemic access differs.
- **Q06 — K:** identical log statement, verified versus materially different unverified provenance. Content held fixed; provenance support differs.
- **Q07 — U:** timeout with unresolved external result versus reliable later non-success. The later signal changes outcome finality, not merely receipt.
- **Q08 — H:** same present condition, different retained recovery histories versus same history. Present state and identity are insufficient to recover retained history.
- **Q09 — O:** first precedes second versus only partial/concurrent ordering justified. Occurrences and content fixed; ordering information differs.
- **Q10 — V:** applicability interval 10–11 versus 12–13. Rule and semantics fixed; temporal validity differs.
- **Q11 — E/S:** issued command changes remote state versus no state change. Attempt held fixed; realized external effect and resulting state diverge.
- **Q12 — U/E:** timeout unresolved versus reliable non-success making retry safe. Attempt and timeout held fixed; outcome certainty/finality differs.
- **Q13 — I:** same reading for same machine versus different machines. Reading held fixed; referent identity differs.
- **Q14 — S:** running then stopped versus running then running. Same machine/times; state transition differs.
- **Q15 — N:** performable maintenance allowed versus rejected. Technical capability held fixed; normative status differs.
- **Q16 — T:** repair allowed and usable equipment versus allowed and unusable equipment. Permission held fixed; equipment enablement differs.
- **Q17 — K:** valve actually closed and uninspected versus closed and inspection received. Fact held fixed; observation/receipt differs.
- **Q18 — K:** same measurement from calibrated versus unverified instrument. Reading held fixed; source verification differs.
- **Q19 — E/U:** command issued with unresolved physical result versus later reliable non-movement. Attempt held fixed; external effect becomes confirmed failure.
- **Q20 — H:** same current machine condition, materially different maintenance histories versus same history. Current state cannot reconstruct retained history.
- **Q21 — O:** evidence of A then B versus insufficient evidence for total order. Records fixed; order/concurrency evidence differs.
- **Q22 — V:** authorization interval one versus a different interval. Authorization content fixed; validity scope differs.
- **Q23 — E/S:** control action causes physical movement versus no movement. Command/attempt held fixed; external effect differs.
- **Q24 — E/U:** timeout with unresolved physical result versus timeout with confirmed non-success. Timeout and attempt held fixed; final outcome differs.
- **Q25 — I:** identical status records same contract versus different contracts. Status held fixed; carrier identity differs.
- **Q26 — S:** active then suspended versus active then active. Same contract/times; state transition differs.
- **Q27 — N:** issuable payment allowed versus rule rejects it. Technical issueability held fixed; permission differs.
- **Q28 — T:** approved transaction with resources available versus unavailable. Approval held fixed; resource enablement differs.
- **Q29 — K:** external signing with no notice versus signed document plus received notice. External fact held fixed; notice/epistemic receipt differs.
- **Q30 — K:** same statement from verified record versus unverified report. Propositional content held fixed; support/provenance differs.
- **Q31 — U/K:** approval sent with completion unresolved versus reliable rejection record. Sending is not completion; outcome finality changes.
- **Q32 — H:** equal contract status, different amendment histories versus equal histories. Current status cannot recover history.
- **Q33 — O:** approval sequence established versus concurrency remains possible. Approval records fixed; order evidence differs.
- **Q34 — V:** approval valid in one interval versus another. Approval identity/content held fixed; temporal scope differs.
- **Q35 — E/S:** instruction issued and external transaction completes versus transaction does not occur. Instruction/attempt held fixed; external realization differs.
- **Q36 — U/K:** timeout with unresolved processing versus later reliable rejection. Same submission/timeout; confirmed outcome replaces uncertainty.

## E. Removal analysis
- Remove **I**: Q01, Q13, Q25 collapse; no state, source, or relation can determine whether equal observations share a referent without hidden identity metadata. **Irreducible.**
- Remove **S**: Q02, Q14, Q26, Q11, Q23 collapse; effects and transitions cannot be reconstructed from permission, attempt, or evidence alone. **Irreducible.**
- Remove **A/E**: Q11, Q19, Q23, Q35 collapse; an attempt cannot entail an external effect. **Irreducible and must remain split.**
- Remove **N**: Q03, Q15, Q27 collapse against technical possibility. **Irreducible.**
- Remove **T**: Q04, Q16, Q28 collapse against permission. **Irreducible.**
- Remove **V**: Q10, Q22, Q34 collapse; an interval is not inferable from content or event order. **Irreducible.**
- Remove **O**: Q09, Q21, Q33 collapse; same records can support precedence or concurrency. **Irreducible relation structure.**
- Remove **K**: Q05, Q06, Q17, Q18, Q29, Q30 collapse; fact, report, receipt, and verification are not interchangeable. **Irreducible.**
- Remove **U**: Q07, Q12, Q24, Q31, Q36 collapse; timeout/unresolved cannot be reconstructed as confirmed rejection/non-success. **Irreducible.**
- Remove **H**: Q08, Q20, Q32 collapse; current equality does not imply historical equality. **Irreducible when retained history is an obligation.**

## F. Merge/split adversarial tests
`N+T` fails: Q03/Q04 vary one while holding the other fixed. `A+E` fails: Q11/Q23/Q35 vary realization while attempt remains fixed. `K+U` fails: Q05/Q17 vary receipt with fact fixed, while Q07/Q12 vary outcome finality. `I+S` fails: Q01/Q13/Q25 hold state/content fixed while identity varies. `V+O` fails: intervals and order are independent. `H+S` fails: Q08/Q20/Q32 hold current state fixed while history varies. Bundling all coordinates as “status”, “constraint”, “metadata”, or an opaque payload violates the composite and anti-laundering rules. Splitting S into every domain noun is not justified by this corpus; open/closed, running/stopped, etc. share a generic current-state role unless an independent case forces domain-specific atoms.

## G. Anti-laundering and carrier analysis
Arbitrary JSON fields, unrestricted predicates, opaque tokens, prose conventions, or a catch-all metadata field would merely hide I/N/T/K/U/H and are rejected. Generic carriers, equality, sets, sequences, and relations may implement identity and order, but the semantic force must be explicit and inspectable. A record with fields is composite if fields vary independently; one object label does not earn one-element minimality. No target vocabulary was imported.

## H. Temporal, causal, concurrency
V is interval validity, not occurrence time. O records precedence or only partial/concurrent order; absence of a total order must not be coerced into sequence. Causal history H is retained content and is not equivalent to O: two histories can have the same order but different maintenance/recovery/amendment causes. The corpus demonstrates only the listed bounded temporal/concurrency distinctions; it does not establish a complete temporal logic.

## I. Epistemic, normative, technical, external effect
K separates external fact, observation/report, receipt, and provenance/verification. U separates unresolved outcome from confirmed success/failure. N (permission) and T (possibility/resources) vary independently. E separates issued action from realized external change; an acknowledgment or record is not itself physical realization. These separations are required by direct counterexamples in Q03/Q04, Q05/Q17, Q07/Q12, and Q11/Q19/Q23/Q35.

## J. Explicit counterexamples against this basis
1. A single “state” with a value `allowed-and-usable` would encode N and T as a bundle; Q03/Q04 and Q15/Q16 falsify atomicity.
2. A single “claim” with a confidence bit would conflate K and U: a verified report can still report an unresolved timeout; Q06/Q07 falsify the merge.
3. A generic event edge could hide either O or causal H; Q09 versus Q08 shows order and retained history vary independently.
4. Identity inferred from equal readings fails Q01/Q13/Q25.
5. Treating command issuance as success fails Q11/Q19/Q23/Q35.
6. Treating missing notice as external non-occurrence fails Q05/Q29.

## K. Omitted-domain / corpus-limit analysis
The corpus does not independently discriminate quantity, spatial geometry, units, resource amounts, actor/role, authorization delegation, data confidentiality, persistence guarantees, or probabilistic degrees beyond unresolved versus reliable confirmation. It also does not prove that S is universally one atom across domains, nor that H is required when history is not retained. These are bounded omissions, not silently reducible dimensions. Generic carrier and relation machinery is assumed available by the contract but cannot carry domain force opaquely.

## L. Bounded verdict and unresolved questions
**Verdict:** PASS for all 36 cases under the supplied contract using the ten-coordinate basis above. The basis is the smallest defensible factorisation I found after adversarial removal and merge attempts; each coordinate has independently varying cases and concrete failure on removal. The result is corpus-relative evidence, not globally minimal ontology proof.

**Explicitly unresolved:** whether a richer corpus would split state, provenance, outcome, or history further; whether retained history should be counted as a primitive or a generic structured carrier under a different obligation set; and whether any alternate factorisation can provide bidirectional mappings without hidden predicates. Those questions are not resolved by this bounded corpus.

## M. Freeze record
- End/freeze time: 2026-09-03T22:05:00+03:00 (recorded immediately before hashing/publication).
- Raw report byte count and SHA-256 are recorded externally after this file was written and must not be changed thereafter.
- Cryptographic commitment: SHA-256 of the exact frozen report bytes (see publication verification metadata).
- No edits or comparative adjudication were performed after the freeze hash.
