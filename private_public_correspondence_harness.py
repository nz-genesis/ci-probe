"""Bounded clean-room harness for private->public semantic correspondence.

The fixture is intentionally generic and contains no Genesis ontology names.
It models a private semantic vector, derives opaque commitments only, and
checks that material private mutations change the public evidence while an
irrelevant private annotation does not. This is a correspondence harness,
not evidence about a real private Genesis vector.
"""
from __future__ import annotations

import hashlib
import hmac
import json

SECRET = b"clean-room-correspondence-test-key-v1"

PRIVATE = {
    "operation": "opaque-op-001",
    "authority": {"principal": "opaque-principal-7", "basis": "basis-17"},
    "lineage": ["opaque-parent-2", "opaque-admission-4"],
    "temporal": {"not_before": 1700000000, "not_after": 1700003600},
    "verification": {"required": True, "class": "effect-confirmation-v1"},
    "effect": {"class": "bounded-external-effect", "footprint": "resource-7"},
    "private_annotation": "must-not-cross-boundary",
}

MATERIAL = ("operation", "authority", "lineage", "temporal", "verification", "effect")
PUBLIC_KEYS = (
    "operation_id",
    "semantic_commitment",
    "authority_commitment",
    "lineage_commitment",
    "temporal_commitment",
    "verification_commitment",
    "effect_commitment",
)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def commitment(value: object) -> str:
    return hmac.new(SECRET, canonical(value), hashlib.sha256).hexdigest()


def derive_public(private: dict) -> dict:
    public = {
        "operation_id": commitment(private["operation"]),
        "semantic_commitment": commitment({k: private[k] for k in MATERIAL}),
    }
    for key in MATERIAL[1:]:
        public[f"{key}_commitment"] = commitment(private[key])
    return public


def verify(private: dict, public: dict) -> bool:
    expected = derive_public(private)
    return public == expected


def mutate(private: dict, key: str, value: object) -> dict:
    copy = json.loads(json.dumps(private))
    copy[key] = value
    return copy


def main() -> int:
    public = derive_public(PRIVATE)

    assertions = [
        ("baseline correspondence", verify(PRIVATE, public)),
        ("public schema contains no raw private values", all(isinstance(public[k], str) for k in PUBLIC_KEYS)),
        ("private annotation excluded from semantic commitment", derive_public(mutate(PRIVATE, "private_annotation", "changed")) == public),
        ("authority mutation detected", not verify(mutate(PRIVATE, "authority", {"principal": "opaque-principal-9", "basis": "basis-17"}), public)),
        ("lineage mutation detected", not verify(mutate(PRIVATE, "lineage", ["opaque-parent-9", "opaque-admission-4"]), public)),
        ("temporal mutation detected", not verify(mutate(PRIVATE, "temporal", {"not_before": 1700000100, "not_after": 1700003600}), public)),
        ("verification mutation detected", not verify(mutate(PRIVATE, "verification", {"required": False, "class": "effect-confirmation-v1"}), public)),
        ("effect mutation detected", not verify(mutate(PRIVATE, "effect", {"class": "bounded-external-effect", "footprint": "resource-9"}), public)),
        ("operation substitution detected", not verify(mutate(PRIVATE, "operation", "opaque-op-002"), public)),
        ("public reconstruction does not expose private fields", set(public).isdisjoint(set(PRIVATE))),
    ]

    failed = [name for name, ok in assertions if not ok]
    print(f"CORRESPONDENCE ASSERTIONS: {len(assertions) - len(failed)}/{len(assertions)} PASS")
    for name, ok in assertions:
        print(f"- {name}: {'PASS' if ok else 'FAIL'}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
