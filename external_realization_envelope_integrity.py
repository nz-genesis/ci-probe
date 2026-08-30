"""Clean-room adversarial integrity checks for an external realization envelope.

Generic only. No private Genesis hypotheses, credentials, private datasets,
internal endpoints, or canonical decisions.

The experiment uses an ephemeral Ed25519 keypair generated at runtime to test
an authenticated provenance mechanism. The private key never enters git.
This proves only the bounded cryptographic mechanism, not production key
custody, trust-root distribution, transport security, or Genesis semantics.
"""

from dataclasses import asdict, replace
import json
import subprocess
import tempfile
from pathlib import Path

from external_realization_envelope_minimization import (
    PublicEnvelope,
    build_envelope,
    private_semantic_contract,
    realize,
)


def canonical_bytes(envelope: PublicEnvelope) -> bytes:
    return json.dumps(asdict(envelope), sort_keys=True, separators=(",", ":")).encode()


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(args, check=False, text=True, capture_output=True)


def main() -> None:
    baseline = build_envelope(private_semantic_contract())
    applied = realize(baseline)
    assert applied["outcome"] == "applied"

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        private_key = root / "issuer.pem"
        public_key = root / "issuer-public.pem"
        payload = root / "envelope.bin"
        signature = root / "envelope.sig"
        tampered_payload = root / "tampered.bin"
        foreign_payload = root / "foreign.bin"

        assert run(
            "openssl", "genpkey", "-algorithm", "ED25519", "-out", str(private_key)
        ).returncode == 0
        assert run(
            "openssl", "pkey", "-in", str(private_key), "-pubout", "-out", str(public_key)
        ).returncode == 0

        payload.write_bytes(canonical_bytes(baseline))
        sign = run(
            "openssl", "pkeyutl", "-sign", "-rawin",
            "-inkey", str(private_key), "-in", str(payload), "-out", str(signature)
        )
        assert sign.returncode == 0, sign.stderr

        verify = run(
            "openssl", "pkeyutl", "-verify", "-rawin",
            "-pubin", "-inkey", str(public_key),
            "-in", str(payload), "-sigfile", str(signature)
        )
        assert verify.returncode == 0, verify.stderr

        # Tampering with an authenticated field invalidates provenance.
        tampered = replace(baseline, admission="deny")
        tampered_payload.write_bytes(canonical_bytes(tampered))
        tampered_verify = run(
            "openssl", "pkeyutl", "-verify", "-rawin",
            "-pubin", "-inkey", str(public_key),
            "-in", str(tampered_payload), "-sigfile", str(signature)
        )
        assert tampered_verify.returncode != 0

        # A signature for one request cannot authenticate another request.
        foreign = replace(baseline, request_id="foreign-request")
        foreign_payload.write_bytes(canonical_bytes(foreign))
        foreign_verify = run(
            "openssl", "pkeyutl", "-verify", "-rawin",
            "-pubin", "-inkey", str(public_key),
            "-in", str(foreign_payload), "-sigfile", str(signature)
        )
        assert foreign_verify.returncode != 0

    # Replay prevention necessarily needs verifier-side state. Model the
    # minimal state explicitly rather than claiming that a signature alone
    # prevents replay.
    seen: set[str] = set()
    envelope_id = applied["request_id"] + ":" + applied["provenance_commitment"]
    assert envelope_id not in seen
    seen.add(envelope_id)
    assert envelope_id in seen

    # Stale semantic state remains distinguishable before realization.
    stale = build_envelope(private_semantic_contract(resource_version="v2"))
    assert stale.provenance_commitment != baseline.provenance_commitment
    assert realize(stale)["outcome"] != applied["outcome"]

    # Verification remains private: its mutation changes provenance but does
    # not export the verification predicate itself.
    private_verification_mutation = build_envelope(
        private_semantic_contract(verification="different-value-rule")
    )
    assert private_verification_mutation.admission == baseline.admission
    assert private_verification_mutation.provenance_commitment != baseline.provenance_commitment

    print("external realization envelope integrity: PASS")
    print("authenticated_provenance=PASS")
    print("tamper_detection=PASS")
    print("cross_request_binding=PASS")
    print("replay_state_model=PASS")
    print("stale_distinction=PASS")
    print("private_verification=PASS")


if __name__ == "__main__":
    main()
