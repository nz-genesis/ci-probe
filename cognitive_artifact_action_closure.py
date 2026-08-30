"""Bounded cognitive/artifact action closure probe.

Clean-room semantic model. It tests that a cognitive capability can be
represented as an executable operation whose result is an artifact with
provenance and verification, without making a particular LLM a Genesis Base
primitive. It deliberately does not claim real LLM determinism or factual
truth.
"""
from dataclasses import dataclass
import hashlib


@dataclass(frozen=True)
class CognitiveContract:
    operation_id: str
    intent: str
    capability: str
    authority: str
    input_root: str
    engine: str
    seed: int
    version: int


@dataclass(frozen=True)
class Artifact:
    content: str
    input_root: str
    operation_id: str
    engine: str
    seed: int
    verified: bool
    provenance: str


def synthesize(c: CognitiveContract) -> Artifact:
    if c.authority != "allow":
        raise PermissionError("authority denied")
    if c.capability != "research-artifact":
        raise ValueError("unsupported cognitive capability")
    if c.version != 1:
        raise ValueError("stale contract")
    # Deterministic surrogate for a cognition engine; engine identity is an
    # implementation parameter, not a Genesis primitive.
    digest = hashlib.sha256(
        f"{c.intent}|{c.input_root}|{c.engine}|{c.seed}".encode()
    ).hexdigest()
    content = f"artifact:{digest}"
    provenance = hashlib.sha256(
        f"{c.operation_id}|{c.input_root}|{digest}".encode()
    ).hexdigest()
    return Artifact(content, c.input_root, c.operation_id, c.engine, c.seed, True, provenance)


def verify(a: Artifact, c: CognitiveContract) -> bool:
    expected = hashlib.sha256(
        f"{c.intent}|{c.input_root}|{c.engine}|{c.seed}".encode()
    ).hexdigest()
    expected_provenance = hashlib.sha256(
        f"{c.operation_id}|{c.input_root}|{expected}".encode()
    ).hexdigest()
    return (
        a.content == f"artifact:{expected}"
        and a.input_root == c.input_root
        and a.operation_id == c.operation_id
        and a.provenance == expected_provenance
        and a.verified
    )


def main() -> None:
    base = CognitiveContract("op-cog-1", "compare sources", "research-artifact", "allow", "root-A", "engine-A", 7, 1)
    a = synthesize(base)
    assert verify(a, base)

    # Same contract + same execution envelope must replay identically.
    assert synthesize(base) == a

    # Engine is replaceable: changing implementation changes artifact bytes,
    # but does not change the Genesis-side contract shape.
    alt = CognitiveContract("op-cog-1", "compare sources", "research-artifact", "allow", "root-A", "engine-B", 7, 1)
    b = synthesize(alt)
    assert verify(b, alt)
    assert b.content != a.content

    # Input authority is causal: changing the input root changes the artifact
    # and its provenance rather than silently reusing the old result.
    changed_input = CognitiveContract("op-cog-1", "compare sources", "research-artifact", "allow", "root-B", "engine-A", 7, 1)
    c = synthesize(changed_input)
    assert c.content != a.content
    assert c.provenance != a.provenance

    # Negative controls.
    try:
        synthesize(CognitiveContract("op-deny", "compare sources", "research-artifact", "deny", "root-A", "engine-A", 7, 1))
    except PermissionError:
        pass
    else:
        raise AssertionError("authority bypass")

    try:
        synthesize(CognitiveContract("op-stale", "compare sources", "research-artifact", "allow", "root-A", "engine-A", 7, 0))
    except ValueError:
        pass
    else:
        raise AssertionError("stale contract accepted")

    # Provenance mutation must be detected.
    tampered = Artifact(a.content, a.input_root, a.operation_id, a.engine, a.seed, a.verified, "tampered")
    assert not verify(tampered, base)

    print("COGNITIVE ARTIFACT ACTION CLOSURE: 9/9 PASS")
    print("Invariant: cognitive capability -> artifact -> provenance -> verification")
    print("No specific cognition engine is required as a Genesis primitive.")


if __name__ == "__main__":
    main()
