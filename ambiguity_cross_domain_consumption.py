"""P192 bounded probe: unresolved semantic alternatives survive domain transfer."""
from dataclasses import dataclass


@dataclass(frozen=True)
class Candidate:
    name: str
    authorized: bool


def consume(envelope, requested_action):
    candidates = envelope["candidates"]
    if len(candidates) != 1:
        if requested_action["safe_for_all_candidates"]:
            return "SAFE_CONSUME"
        return "UNRESOLVED"
    if not candidates[0].authorized:
        return "UNAUTHORIZED"
    return "CONSUME"


def main():
    a = {"name": "A", "authorized": True}
    b = {"name": "B", "authorized": True}
    u = {"name": "U", "authorized": False}

    cases = [
        ("unique authorized", {"candidates": [a]}, {"safe_for_all_candidates": False}, "CONSUME"),
        ("ambiguous unsafe", {"candidates": [a, b]}, {"safe_for_all_candidates": False}, "UNRESOLVED"),
        ("ambiguous universally safe", {"candidates": [a, b]}, {"safe_for_all_candidates": True}, "SAFE_CONSUME"),
        ("authorized plus unauthorized remains ambiguous", {"candidates": [a, u]}, {"safe_for_all_candidates": False}, "UNRESOLVED"),
        ("unauthorized unique", {"candidates": [u]}, {"safe_for_all_candidates": False}, "UNAUTHORIZED"),
    ]
    for label, envelope, action, expected in cases:
        got = consume(envelope, action)
        assert got == expected, f"{label}: expected {expected}, got {got}"

    print("AMBIGUITY CROSS-DOMAIN CONSUMPTION: 5/5 PASS")


if __name__ == "__main__":
    main()
