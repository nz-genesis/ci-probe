"""Bounded adaptive-observation probe for private/public noninterference."""
from dataclasses import dataclass

@dataclass(frozen=True)
class State:
    public_status: str
    public_version: int
    private_secret: str
    private_score: int


def safe_query(state: State, query: str) -> str:
    if query == "summary":
        return f"{state.public_status}:{state.public_version}"
    if query == "detail" and state.public_status == "ready":
        return "ready-detail"
    return "not-available"


def unsafe_query(state: State, query: str) -> str:
    if query == "summary":
        return f"{state.public_status}:{state.public_version}"
    if query == "detail" and state.public_status == "ready":
        # Adversarial implementation: private data enters a public response.
        return f"ready-detail:{state.private_score % 2}"
    return "not-available"


def adaptive_transcript(query_fn, state: State) -> tuple[tuple[str, str], ...]:
    transcript = []
    first = query_fn(state, "summary")
    transcript.append(("summary", first))
    next_query = "detail" if first.startswith("ready:") else "not-available"
    transcript.append((next_query, query_fn(state, next_query)))
    return tuple(transcript)


def main() -> None:
    base = State("ready", 1, "secret-A", 10)
    private_changed = State("ready", 1, "secret-B", 11)
    public_changed = State("blocked", 1, "secret-A", 10)

    # Adaptive observation must remain noninterfering for private-only changes.
    assert adaptive_transcript(safe_query, base) == adaptive_transcript(safe_query, private_changed)

    # Public semantic changes remain observable even through adaptive observation.
    assert adaptive_transcript(safe_query, base) != adaptive_transcript(safe_query, public_changed)

    # Red Team: the adaptive observer exposes the leak in an unsafe projection.
    assert adaptive_transcript(unsafe_query, base) != adaptive_transcript(unsafe_query, private_changed)

    # The first query is identical, so the leak arises only after the observer adapts.
    safe_base = adaptive_transcript(safe_query, base)
    unsafe_base = adaptive_transcript(unsafe_query, base)
    assert safe_base[0] == unsafe_base[0]
    assert safe_base[1][0] == unsafe_base[1][0] == "detail"
    assert safe_base[1][1] != unsafe_base[1][1]

    print("ADAPTIVE PUBLIC OBSERVATION: 6/6 PASS")
    print("Invariant: private-only changes do not alter adaptive public transcripts")

if __name__ == "__main__":
    main()
