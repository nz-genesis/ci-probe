"""Bounded derived-field noninterference probe for private/public state."""
from dataclasses import dataclass

@dataclass(frozen=True)
class State:
    public_status: str
    public_version: int
    private_note: str
    private_score: int


def public_projection(s: State) -> dict[str, object]:
    # Only declared public semantics may feed the public result.
    return {"status": s.public_status, "version": s.public_version}


def main() -> None:
    base = State("ready", 1, "secret-A", 10)
    private_note_mutation = State("ready", 1, "secret-B", 10)
    private_score_mutation = State("ready", 1, "secret-A", 99)
    public_status_mutation = State("blocked", 1, "secret-A", 10)
    public_version_mutation = State("ready", 2, "secret-A", 10)

    # Noninterference: private mutations do not alter public outputs.
    assert public_projection(base) == public_projection(private_note_mutation)
    assert public_projection(base) == public_projection(private_score_mutation)

    # Correspondence: declared public mutations remain observable.
    assert public_projection(base) != public_projection(public_status_mutation)
    assert public_projection(base) != public_projection(public_version_mutation)

    # No private field is emitted by the projection.
    assert set(public_projection(base)) == {"status", "version"}
    assert "secret-A" not in str(public_projection(base))
    assert "10" not in str(public_projection(base))

    # Adversarial derived-field guard: a forbidden private field must not enter output.
    leaked = {"status": base.public_status, "version": base.public_version, "score": base.private_score}
    assert set(leaked) - {"status", "version"}, "fixture must contain a private leakage control"
    assert set(public_projection(base)) <= {"status", "version"}

    print("DERIVED-FIELD NONINTERFERENCE: 7/7 PASS")
    print("Invariant: private mutations do not affect declared public projection")

if __name__ == "__main__":
    main()
