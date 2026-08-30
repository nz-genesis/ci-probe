"""Bounded test: temporal validity + authority + contradiction handling.

This is a semantic surrogate, not a claim about external source authenticity.
"""
from dataclasses import dataclass

@dataclass(frozen=True)
class Source:
    sid: str
    authority: int
    valid_from: int
    valid_until: int
    facts: tuple[tuple[str, str], ...]


def valid(s: Source, t: int) -> bool:
    return s.valid_from <= t <= s.valid_until


def admit(sources: list[Source], now: int, claim: tuple[str, str]) -> bool:
    candidates = [s for s in sources if valid(s, now) and claim in s.facts]
    if not candidates:
        return False
    # A claim is admitted only when no higher-authority valid source contradicts it.
    opposite = (claim[0], "false" if claim[1] == "true" else "true")
    opposing = [s for s in sources if valid(s, now) and opposite in s.facts]
    if opposing and max(s.authority for s in opposing) >= max(s.authority for s in candidates):
        return False
    return True


def main() -> None:
    current = Source("current", 3, 0, 20, (("alpha", "true"),))
    stale = Source("stale", 4, 0, 5, (("alpha", "false"),))
    lower_conflict = Source("lower", 1, 0, 20, (("alpha", "false"),))
    future = Source("future", 4, 11, 20, (("beta", "true"),))

    checks = {
        "current claim admitted": admit([current, stale], 10, ("alpha", "true")),
        "stale contradiction ignored": admit([current, stale], 10, ("alpha", "true")),
        "lower authority contradiction does not veto": admit([current, lower_conflict], 10, ("alpha", "true")),
        "future source not admitted early": not admit([future], 10, ("beta", "true")),
        "future source admitted when valid": admit([future], 11, ("beta", "true")),
        "stale source cannot create claim": not admit([stale], 10, ("alpha", "false")),
        "equal-authority contradiction blocks": not admit([current, Source("peer", 3, 0, 20, (("alpha", "false"),))], 10, ("alpha", "true")),
        "unsupported claim rejected": not admit([current], 10, ("gamma", "true")),
    }
    assert all(checks.values()), checks
    print(f"TEMPORAL AUTHORITATIVE EVIDENCE: {sum(checks.values())}/{len(checks)} PASS")

if __name__ == "__main__":
    main()
