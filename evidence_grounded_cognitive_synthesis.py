"""Bounded evidence-grounded cognitive synthesis probe for Genesis.

Clean-room semantic model. It tests source-bounded claim production, provenance,
contradiction handling, stale-source rejection, and removal witnesses without
making an LLM or retrieval engine a Genesis primitive.
"""
from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class Source:
    source_id: str
    root: str
    version: int
    facts: tuple[tuple[str, str], ...]
    authority: str = "allowed"


@dataclass(frozen=True)
class Claim:
    claim_id: str
    subject: str
    predicate: str
    value: str
    source_ids: tuple[str, ...]
    input_root: str
    synthesis_version: int


def root(sources: tuple[Source, ...]) -> str:
    material = "|".join(
        f"{s.source_id}:{s.version}:{s.facts}" for s in sorted(sources, key=lambda x: x.source_id)
    )
    return sha256(material.encode()).hexdigest()


def synthesize(sources: tuple[Source, ...], synthesis_version: int = 1) -> tuple[Claim, ...]:
    if not sources:
        raise ValueError("evidence set is empty")
    if any(s.authority != "allowed" for s in sources):
        raise PermissionError("unauthorized evidence source")
    by_subject: dict[str, set[str]] = {}
    for source in sources:
        for subject, value in source.facts:
            by_subject.setdefault(subject, set()).add(value)
    claims: list[Claim] = []
    evidence_root = root(sources)
    for subject, values in sorted(by_subject.items()):
        if len(values) != 1:
            raise ValueError(f"contradictory evidence for {subject}")
        value = next(iter(values))
        ids = tuple(s.source_id for s in sources if any(x == subject and y == value for x, y in s.facts))
        claims.append(Claim(f"c-{subject}", subject, "value", value, ids, evidence_root, synthesis_version))
    return tuple(claims)


def verify(claims: tuple[Claim, ...], sources: tuple[Source, ...]) -> None:
    expected_root = root(sources)
    allowed = {s.source_id for s in sources if s.authority == "allowed"}
    facts = {(subject, value) for s in sources if s.authority == "allowed" for subject, value in s.facts}
    for claim in claims:
        assert claim.input_root == expected_root, "claim input root mismatch"
        assert claim.source_ids, "claim has no provenance"
        assert set(claim.source_ids) <= allowed, "claim cites unauthorized source"
        assert (claim.subject, claim.value) in facts, "unsupported claim"


def main() -> None:
    a = Source("A", "corpus-A", 1, (("alpha", "verified"), ("beta", "present")))
    b = Source("B", "corpus-B", 1, (("alpha", "verified"),))
    sources = (a, b)
    claims = synthesize(sources)
    verify(claims, sources)

    # Causal input sensitivity: removing B changes the evidence root but not the supported alpha value.
    reduced = (a,)
    reduced_claims = synthesize(reduced)
    verify(reduced_claims, reduced)
    assert reduced_claims[0].input_root != claims[0].input_root

    # Unsupported claim cannot pass independent verification.
    forged = Claim("c-forged", "alpha", "value", "invented", ("A",), root(sources), 1)
    try:
        verify((forged,), sources)
    except AssertionError:
        pass
    else:
        raise AssertionError("unsupported claim accepted")

    # Unauthorized evidence cannot enter synthesis.
    denied = Source("X", "external", 1, (("gamma", "secret"),), "denied")
    try:
        synthesize((a, denied))
    except PermissionError:
        pass
    else:
        raise AssertionError("unauthorized evidence accepted")

    # Contradiction must remain explicit rather than being silently resolved.
    contradiction = Source("C", "corpus-C", 1, (("alpha", "false"),))
    try:
        synthesize((a, contradiction))
    except ValueError:
        pass
    else:
        raise AssertionError("contradictory evidence silently resolved")

    # Stale/tampered provenance: same claim with a changed evidence root must fail.
    tampered = Claim(claims[0].claim_id, claims[0].subject, claims[0].predicate,
                     claims[0].value, claims[0].source_ids, root(reduced), claims[0].synthesis_version)
    try:
        verify((tampered,), sources)
    except AssertionError:
        pass
    else:
        raise AssertionError("tampered provenance accepted")

    # Removal witness: beta is causally dependent on source A.
    beta_full = next(c for c in claims if c.subject == "beta")
    assert "A" in beta_full.source_ids
    assert all(c.subject != "beta" for c in reduced_claims)

    print("EVIDENCE-GROUNDED COGNITIVE SYNTHESIS: 8/8 PASS")
    print("Invariant: evidence-bounded synthesis -> claim provenance -> independent verification")
    print("No cognition/retrieval/LLM-specific Genesis primitive is introduced.")


if __name__ == "__main__":
    main()
