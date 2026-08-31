"""P193 bounded probe: lossy semantic transfer must not create false uniqueness."""


def consume(transfer, action):
    if transfer["decision_relevant_information_lost"]:
        if action["safe_for_all_source_candidates"]:
            return "SAFE_CONSUME"
        return "UNRESOLVED"
    candidates = transfer["target_candidates"]
    if len(candidates) != 1:
        return "UNRESOLVED"
    if not candidates[0]["authorized"]:
        return "UNAUTHORIZED"
    return "CONSUME"


def main():
    a = {"name": "A", "authorized": True}
    b = {"name": "B", "authorized": True}
    u = {"name": "U", "authorized": False}

    cases = [
        (
            "lossless unique",
            {"source_candidates": [a], "target_candidates": [a], "decision_relevant_information_lost": False},
            {"safe_for_all_source_candidates": False},
            "CONSUME",
        ),
        (
            "lossy collapse creates false uniqueness",
            {"source_candidates": [a, b], "target_candidates": [a], "decision_relevant_information_lost": True},
            {"safe_for_all_source_candidates": False},
            "UNRESOLVED",
        ),
        (
            "lossy but action invariant for all source candidates",
            {"source_candidates": [a, b], "target_candidates": [a], "decision_relevant_information_lost": True},
            {"safe_for_all_source_candidates": True},
            "SAFE_CONSUME",
        ),
        (
            "irrelevant information loss",
            {"source_candidates": [a], "target_candidates": [a], "decision_relevant_information_lost": False},
            {"safe_for_all_source_candidates": False},
            "CONSUME",
        ),
        (
            "forged unique target from multiple source candidates",
            {"source_candidates": [a, u], "target_candidates": [a], "decision_relevant_information_lost": True},
            {"safe_for_all_source_candidates": False},
            "UNRESOLVED",
        ),
        (
            "observation restores distinction",
            {"source_candidates": [a, b], "target_candidates": [a], "decision_relevant_information_lost": False},
            {"safe_for_all_source_candidates": False},
            "CONSUME",
        ),
        (
            "lossless unique unauthorized",
            {"source_candidates": [u], "target_candidates": [u], "decision_relevant_information_lost": False},
            {"safe_for_all_source_candidates": False},
            "UNAUTHORIZED",
        ),
    ]

    for label, transfer, action, expected in cases:
        got = consume(transfer, action)
        assert got == expected, f"{label}: expected {expected}, got {got}"

    print("LOSSY SEMANTIC TRANSFER: 7/7 PASS")


if __name__ == "__main__":
    main()
