"""P312: concrete credential/trust-boundary realization.

This fixture uses Ed25519 signatures over canonical credential payloads. A
protected root signs an owner credential; the owner signs an attenuated child
credential. Verification walks that chain, enforces scope attenuation,
current epoch/policy/cache generation, and rejects verifier substitution,
credential tampering, stale credentials, replay, and escalation. Cognition is
only an input selector and never an authority source.
"""
import base64
import hashlib
import json
from itertools import product

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

CURRENT_EPOCH = 7
CURRENT_POLICY = "policy-v3"
CURRENT_CACHE = 11
ROOT_SCOPE = frozenset({"read", "write:task"})
OWNER_SCOPE = frozenset({"read", "write:task"})
CHILD_SCOPE = frozenset({"read"})


def canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def key(seed):
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(seed.encode()).digest())


def issue(signer, subject, scope, epoch, parent_subject=None, parent_pub=None):
    payload = {
        "subject": subject,
        "scope": sorted(scope),
        "epoch": epoch,
        "policy": CURRENT_POLICY,
        "parent_subject": parent_subject,
        "parent_pub": parent_pub,
    }
    return {
        "payload": payload,
        "sig": base64.b64encode(signer.sign(canonical(payload))).decode(),
        "pub": base64.b64encode(signer.public_key().public_bytes_raw()).decode(),
    }


def verify_chain(root_public, owner_cred, child_cred, required_scope, epoch, policy, cache, expected_cache):
    if cache != expected_cache:
        return False
    owner = owner_cred["payload"]
    child = child_cred["payload"]
    if owner["epoch"] != epoch or child["epoch"] != epoch:
        return False
    if owner["policy"] != policy or child["policy"] != policy:
        return False
    if not set(child["scope"]).issubset(set(owner["scope"])):
        return False
    if not set(required_scope).issubset(set(child["scope"])):
        return False
    try:
        root_public.verify(base64.b64decode(owner_cred["sig"]), canonical(owner))
        owner_public = base64.b64decode(owner_cred["pub"])
        # Child must bind to exactly the public key certified by the owner credential.
        if child["parent_pub"] != base64.b64encode(owner_public).decode():
            return False
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
        Ed25519PublicKey.from_public_bytes(owner_public).verify(
            base64.b64decode(child_cred["sig"]), canonical(child)
        )
    except Exception:
        return False
    return True


def main():
    root = key("genesis-root")
    owner = key("owner")
    attacker = key("attacker")
    owner_pub = base64.b64encode(owner.public_key().public_bytes_raw()).decode()
    owner_cred = issue(root, "owner", OWNER_SCOPE, CURRENT_EPOCH)
    child = issue(owner, "delegate", CHILD_SCOPE, CURRENT_EPOCH, "owner", owner_pub)

    checked = allowed = unsafe = 0
    for epoch, policy, cache, child_kind, required, verifier_kind, cognition in product(
        (CURRENT_EPOCH, CURRENT_EPOCH - 1),
        (CURRENT_POLICY, "policy-old"),
        (CURRENT_CACHE, CURRENT_CACHE - 1),
        ("valid", "scope_escalated", "replayed", "forged_parent"),
        ("read", "write:task"),
        ("protected", "substituted"),
        ("strong", "weak_adversarial"),
    ):
        checked += 1
        candidate = dict(child)
        if child_kind == "scope_escalated":
            candidate["payload"] = dict(child["payload"], scope=["read", "write:task"])
        elif child_kind == "replayed":
            candidate["payload"] = dict(child["payload"], epoch=CURRENT_EPOCH - 1)
        elif child_kind == "forged_parent":
            candidate["payload"] = dict(child["payload"], parent_pub=base64.b64encode(attacker.public_key().public_bytes_raw()).decode())
        verifier = root.public_key() if verifier_kind == "protected" else attacker.public_key()
        ok = verify_chain(verifier, owner_cred, candidate, required, epoch, policy, cache, CURRENT_CACHE)
        if ok:
            allowed += 1
        attack = (
            epoch != CURRENT_EPOCH or policy != CURRENT_POLICY or cache != CURRENT_CACHE
            or child_kind != "valid" or verifier_kind != "protected" or required == "write:task"
        )
        if attack and ok:
            unsafe += 1
    assert checked == 256
    assert unsafe == 0
    assert allowed == 2
    print(f"P312 credential trust-boundary matrix: {checked}/{checked} PASS")
    print(f"allowed={allowed}; blocked={checked-allowed}; unsafe={unsafe}")


if __name__ == "__main__":
    main()
