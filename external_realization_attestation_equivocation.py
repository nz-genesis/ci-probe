"""Bounded clean-room test for attestation equivocation.

The same authority can authenticate two different semantic envelopes for the
same request/nonce/context. Signature validity and receipt binding alone do
not reveal that equivocation; a consistency/observation state is required.
This is generic boundary evidence, not Genesis ontology.
"""
from dataclasses import dataclass
from hashlib import sha256
import hmac

KEY = b"clean-room-equivocation-key-v1"


@dataclass(frozen=True)
class Envelope:
    authority: str
    request_id: str
    nonce: str
    epoch: int
    semantic_digest: str


@dataclass(frozen=True)
class Attestation:
    envelope_digest: str
    signature: str


def digest(*values: object) -> str:
    return sha256("|".join(map(str, values)).encode()).hexdigest()


def envelope_digest(envelope: Envelope) -> str:
    return digest(
        envelope.authority,
        envelope.request_id,
        envelope.nonce,
        envelope.epoch,
        envelope.semantic_digest,
    )


def attest(envelope: Envelope) -> Attestation:
    d = envelope_digest(envelope)
    return Attestation(d, hmac.new(KEY, d.encode(), "sha256").hexdigest())


def authentic(envelope: Envelope, attestation: Attestation) -> bool:
    d = envelope_digest(envelope)
    expected = hmac.new(KEY, d.encode(), "sha256").hexdigest()
    return d == attestation.envelope_digest and hmac.compare_digest(expected, attestation.signature)


def guarded_accept(
    envelope: Envelope,
    attestation: Attestation,
    observed: dict[tuple[str, str, str, int], str],
) -> tuple[bool, str]:
    if not authentic(envelope, attestation):
        return False, "BAD_ATTESTATION"
    key = (envelope.authority, envelope.request_id, envelope.nonce, envelope.epoch)
    prior = observed.get(key)
    current = attestation.envelope_digest
    if prior is not None and prior != current:
        return False, "AUTHORITY_EQUIVOCATION"
    observed[key] = current
    return True, "ACCEPTED"


def main() -> None:
    e1 = Envelope("authority-A", "request-7", "nonce-7", 11, "semantic-E1")
    e2 = Envelope("authority-A", "request-7", "nonce-7", 11, "semantic-E2")
    a1 = attest(e1)
    a2 = attest(e2)

    # Both statements are independently authentic. A verifier with no
    # consistency state cannot distinguish equivocation from two valid claims.
    assert authentic(e1, a1)
    assert authentic(e2, a2)
    assert a1.envelope_digest != a2.envelope_digest

    assert authentic(e1, a1) and authentic(e2, a2), "naive authenticity must accept both"

    observed: dict[tuple[str, str, str, int], str] = {}
    assert guarded_accept(e1, a1, observed) == (True, "ACCEPTED")
    assert guarded_accept(e2, a2, observed) == (False, "AUTHORITY_EQUIVOCATION")

    # Same statement is not an equivocation and remains acceptable.
    assert guarded_accept(e1, a1, observed) == (True, "ACCEPTED")

    print("ATTESTATION EQUIVOCATION BOUNDARY: 6/6 PASS")
    print("authenticated_conflicting_statements: PASS")
    print("consistency_guard_detects_equivocation: PASS")
    print("finding: authenticity_and_receipt_binding_do_not_by_themselves_prove_authority_consistency")


if __name__ == "__main__":
    main()
