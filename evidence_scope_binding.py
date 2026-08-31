"""P203 — Compatibility-evidence scope binding.

A compatibility claim is usable only when the evidence scope covers the
required decision scope. Scope mismatch must fail closed.
"""


def covers(evidence_scope: dict, required_scope: dict) -> bool:
    return all(evidence_scope.get(k) == v for k, v in required_scope.items())


def decide(evidence_scope: dict, required_scope: dict) -> str:
    return "ACCEPT" if covers(evidence_scope, required_scope) else "REJECT"


BASE = {
    "schema": "A->B",
    "resource": "r1",
    "action": "read",
    "policy": "p1",
    "version": "v1",
}

CASES = [
    ("exact_scope", BASE, BASE, "ACCEPT"),
    ("resource_widening", BASE, {**BASE, "resource": "r2"}, "REJECT"),
    ("action_widening", BASE, {**BASE, "action": "write"}, "REJECT"),
    ("policy_change", BASE, {**BASE, "policy": "p2"}, "REJECT"),
    ("version_change", BASE, {**BASE, "version": "v2"}, "REJECT"),
    ("schema_change", BASE, {**BASE, "schema": "A->C"}, "REJECT"),
    ("missing_evidence_scope", {k: v for k, v in BASE.items() if k != "resource"}, BASE, "REJECT"),
    ("extra_evidence_scope_but_required_subset", {**BASE, "tenant": "t1"}, BASE, "ACCEPT"),
]


for name, evidence_scope, required_scope, expected in CASES:
    actual = decide(evidence_scope, required_scope)
    assert actual == expected, f"{name}: expected {expected}, got {actual}"

# Red-team: stripping scope must never preserve an ACCEPT decision.
stripped = {k: v for k, v in BASE.items() if k not in {"resource", "action"}}
assert decide(stripped, BASE) == "REJECT"

# Red-team: evidence valid for read must not authorize write.
assert decide(BASE, {**BASE, "action": "write"}) == "REJECT"

print(f"EVIDENCE SCOPE BINDING: {len(CASES) + 2}/{len(CASES) + 2} PASS")
