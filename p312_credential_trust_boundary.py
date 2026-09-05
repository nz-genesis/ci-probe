"""P312: concrete credential/trust-boundary realization.

Ed25519 credentials are canonical signed objects. The protected root signs an
owner credential whose payload binds the owner's public key; the owner signs
an attenuated child credential bound to that certified key. Verification
requires the protected root, valid delegation chain, scope attenuation,
current epoch/policy/cache generation, and rejects substitution, tampering,
replay and escalation. Cognition is only a selector, never an authority
source. Cryptography is a realization mechanism, not a new Genesis primitive.
"""
import base64
import hashlib
import json
from itertools import product

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey

CURRENT_EPOCH = 7
CURRENT_POLICY = "policy-v3"
CURRENT_CACHE = 11
OWNER_SCOPE = frozenset({"read", "write:task"})
CHILD_SCOPE = frozenset({"read"})


def canonical(payload):
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()


def key(seed):
    return Ed25519PrivateKey.from_private_bytes(hashlib.sha256(seed.encode()).digest())


def pub64(private):
    return base64.b64encode(private.public_key().public_bytes_raw()).decode()


def issue(signer, subject, subject_pub, scope, epoch, parent_subject=None, parent_pub=None):
    payload = {
        "subject": subject,
        "subject_pub": subject_pub,
        "scope": sorted(scope),
        "epoch": epoch,
        "policy": CURRENT_POLICY,
        "parent_subject": parent_subject,
        "parent_pub": parent_pub,
    }
    return {"payload": payload, "sig": base64.b64encode(signer.sign(canonical(payload))).decode()}


def verify_chain(root_public, owner_cred, child_cred, required_scope, epoch, policy, cache, expected_cache):
    if cache != expected_cache:
        return False
    owner = owner_cred["payload"]
    child = child_cred["payload"]
    if owner["epoch"] != epoch or child["epoch"] != epoch:
        return False
    if owner["policy"] != policy or child["policy"] != policy:
        return False
    if child["parent_subject"] != owner["subject"]:
        return False
    if child["parent_pub"] != owner["subject_pub"]:
        return False
    if not set(child["scope"]).issubset(set(owner["scope"])):
        return False
    if not set(required_scope).issubset(set(child["scope"])):
        return False
    try:
        root_public.verify(base64.b64decode(owner_cred["sig"]), canonical(owner))
        owner_public = Ed25519PublicKey.from_public_bytes(base64.b64decode(owner["subject_pub"]))
        owner_public.verify(base64.b64decode(child_cred["sig"]), canonical(child))
    except Exception:
        return False
    return True


def main():
    root = key("genesis-root")
    owner = key("owner")
    attacker = key("attacker")
    owner_pub = pub64(owner)
    owner_cred = issue(root, "owner", owner_pub, OWNER_SCOPE, CURRENT_EPOCH)
    child = issue(owner, "delegate", pub64(key("delegate")), CHILD_SCOPE, CURRENT_EPOCH, "owner", owner_pub)

    checked = allowed = unsafe = 0
    for epoch, policy, cache, child_kind, required, verifier_kind, cognition in product(
        (CURRENT_EPOCH, CURRENT_EPOCH - 1),
        (CURRENT_POLICY, "policy-old"),
        (CURRENT_CACHE, CURRENT_CACHE - 1),
        ("valid", "scope_escalated", "replayed", "forged_parent", "forged_owner_key"),
        ("read", "write:task"),
        ("protected", "substituted"),
        ("strong", "weak_adversarial"),
    ):
        checked += 1
        owner_candidate = dict(owner_cred)
        owner_candidate["payload"] = dict(owner_cred["payload"])
        candidate = dict(child)
        candidate["payload"] = dict(child["payload"])
        if child_kind == "scope_escalated":
            candidate["payload"]["scope"] = ["read", "write:task"]
        elif child_kind == "replayed":
            candidate["payload"]["epoch"] = CURRENT_EPOCH - 1
        elif child_kind == "forged_parent":
            candidate["payload"]["parent_pub"] = pub64(attacker)
        elif child_kind == "forged_owner_key":
            owner_candidate["payload"]["subject_pub"] = pub64(attacker)
        verifier = root.public_key() if verifier_kind == "protected" else attacker.public_key()
        ok = verify_chain(verifier, owner_candidate, candidate, required, epoch, policy, cache, CURRENT_CACHE)
        if ok:
            allowed += 1
        attack = (
            epoch != CURRENT_EPOCH or policy != CURRENT_POLICY or cache != CURRENT_CACHE
            or child_kind != "valid" or verifier_kind != "protected" or required == "write:task"
        )
        if attack and ok:
            unsafe += 1
    assert checked == 320
    assert unsafe == 0
    assert allowed == 2
    print(f"P312 credential trust-boundary matrix: {checked}/{checked} PASS")
    print(f"allowed={allowed}; blocked={checked-allowed}; unsafe={unsafe}")


if __name__ == "__main__":
    main()
