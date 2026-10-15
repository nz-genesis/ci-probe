# External effect × crash window × reconciliation

## Question

After an irreversible external effect is initiated, can the semantic state of authority, transition, acknowledgement, effect evidence and reconciliation remain distinct without introducing `Execution`, `Recovery`, `Transaction` or `Action` as universal primitives?

## Competing hypotheses

- **H1 — reduced representation is sufficient:** effect existence is established by effect evidence; recovery is reconciliation over state/evidence.
- **H2 — execution/recovery is irreducible:** a dedicated execution or recovery primitive is required to preserve the distinction.
- **H3 — acknowledgement proves effect:** an acknowledgement can be treated as sufficient verification of the external effect.
- **H4 — revocation erases an initiated effect:** revocation after initiation can be treated as evidence that no effect occurred.

## Bounded model

The record contains four independent dimensions:

```text
authority
transition state
effect evidence
acknowledgement
```

Reconciliation derives the epistemic effect status:

```text
NO_EFFECT_KNOWN
EFFECT_CONFIRMED
EFFECT_ABSENT
EFFECT_UNKNOWN
EFFECT_CONFLICTING
```

These are derived classifications, not proposed Genesis primitives.

## Scenarios

1. valid authority → initiation → crash → lost acknowledgement → no effect evidence;
2. effect occurred → acknowledgement lost → authority later revoked;
3. explicit non-effect evidence;
4. conflicting effect evidence;
5. acknowledgement without effect evidence;
6. no initiation.

## Observed result

The bounded model preserves the crucial distinctions:

```text
initiated + no effect evidence       → EFFECT_UNKNOWN
initiated + occurrence evidence      → EFFECT_CONFIRMED
initiated + explicit absence evidence→ EFFECT_ABSENT
initiated + conflicting evidence     → EFFECT_CONFLICTING
ack alone                            → EFFECT_UNKNOWN
```

Revocation after initiation does not retroactively establish non-occurrence. Likewise, missing evidence is not converted into evidence of absence.

## Primitive-removal result

The experiment does not require separate universal primitives for:

```text
Execution
Recovery
Transaction
Action
```

The semantic distinctions are representable using transition state, authority state, effect evidence, acknowledgement and reconciliation rules.

This is not a proof that no specialized transactional mechanism can ever be required in an implementation. It only rejects the inference that a named implementation mechanism is automatically a Genesis primitive.

## Red Team

- **ACK laundering:** rejected; acknowledgement alone remains UNKNOWN.
- **Revocation laundering:** rejected; post-initiation revocation does not erase effect evidence.
- **Absence laundering:** rejected; no evidence ≠ evidence of absence.
- **Recovery laundering:** recovery is modeled as reconciliation; no dedicated primitive is required in this bounded fixture.
- **External-world overclaim:** open; the experiment models evidence of an external effect, not an actual physical effect.
- **Crash realism:** open; process crash is represented abstractly, not with a real distributed crash/restart system.
- **Transaction semantics:** open; atomic multi-resource commit/rollback is not modeled.

## Limitations

No real external system, network partition, durable storage, process crash, physical actuator, exactly-once guarantee, or distributed transaction protocol is executed here.

## Public boundary

Generic clean-room experiment only. No private Genesis architecture, credentials, internal endpoints, datasets or canonical decisions are included.
