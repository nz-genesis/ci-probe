from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True)
class State:
    public_status: str
    private_score: int
    private_note: str


def safe_transcript(state: State):
    """Public semantics depend only on declared public state."""
    first = ("summary", state.public_status)
    if first[1] == "ready":
        second = ("detail", "ready-detail")
        third = ("audit", sha256("ready-detail".encode()).hexdigest()[:8])
        return (first, second, third)
    return (first, ("audit", "not-ready"), ("end",))


def unsafe_transcript(state: State):
    """Red-team implementation: private state contaminates an intermediate value."""
    first = ("summary", state.public_status)
    if first[1] == "ready":
        derived = "high" if state.private_score >= 50 else "low"
        second = ("detail", derived)
        third = ("audit", sha256(derived.encode()).hexdigest()[:8])
        return (first, second, third)
    return (first, ("audit", "not-ready"), ("end",))


def main():
    base = State("ready", 10, "A")
    private_mutation = State("ready", 90, "B")
    public_mutation = State("paused", 10, "A")

    # Private-only changes do not alter the safe adaptive transcript.
    assert safe_transcript(base) == safe_transcript(private_mutation)

    # Public changes remain observable.
    assert safe_transcript(base) != safe_transcript(public_mutation)

    # The adversarial implementation is caught even though the first response is equal.
    assert unsafe_transcript(base) != unsafe_transcript(private_mutation)
    assert unsafe_transcript(base)[0] == unsafe_transcript(private_mutation)[0]
    assert unsafe_transcript(base)[1] != unsafe_transcript(private_mutation)[1]
    assert unsafe_transcript(base)[2] != unsafe_transcript(private_mutation)[2]

    print("ADAPTIVE TRANSITIVE OBSERVATION: 6/6 PASS")


if __name__ == "__main__":
    main()

# Verification checkpoint: semantic logic unchanged; this commit intentionally retriggers hosted CI for post-write verification.
