"""P193 bounded probe: lossy semantic transfer must not create false uniqueness."""


def consume(transfer, action):
    if transfer["decision_relevant_information_lost"]:
        if action["safe_for_all_source_candidates"]:
            return "SAFE_CONSUME"
        return "UNRESOLVED"

    source = transfer["source_candidates"]
    target = transfer["target_candidates"]
    if len(source) != 1 and not transfer["observation_validated"]:
        if action["safe_for_all_source_candidates"]:
            return "SAFE_CONSUME"
        return "UNRESOLVED"
    if len(target) != 1:
        return "UNRESOLVED"
    if not target[0]["authorized"]:
        return "UNAUTHORIZED"
    return "CONSUME"


def main():
    a = {"name": "A", "authorized": True}
    b = {"name": "B", "authorized": True}
    u = {"name": "U", "authorized": False}

    cases = [
        ("lossless unique", {"source_candidates": [a], "target_candidates": [a], "decision_relevant_information_lost": False, "observation_validated": False}, {"safe_for_all_source_candidates": False}, "CONSUME"),
        ("lossy collapse creates false uniqueness", {"source_candidates": [a, b], "target_candidates": [a], "decision_relevant_information_lost": True, "observation_validated": False}, {"safe_for_all_source_candidates": False}, "UNRESOLVED"),
        ("lossy but action invariant for all source candidates", {"source_candidates": [a, b], "target_candidates": [a], "decision_relevant_information_lost": True, "observation_validated": False}, {"safe_for_all_source_candidates": True}, "SAFE_CONSUME"),
        ("irrelevant information loss", {"source_candidates": [a], "target_candidates": [a], "decision_relevant_information_lost": False, "observation_validated": False}, {"safe_for_all_source_candidates": False}, "CONSUME"),
        ("forged unique target from multiple source candidates", {"source_candidates": [a, u], "target_candidates": [a], "decision_relevant_information_lost": False, "observation_validated": False}, {"safe_for_all_source_candidates": False}, "UNRESOLVED"),
        ("validated observation restores distinction", {"source_candidates": [a, b], "target_candidates": [a], "decision_relevant_information_lost": False, "observation_validated": True}, {"safe_for_all_source_candidates": False}, "CONSUME"),
        ("lossy multiple targets universally safe", {"source_candidates": [a, b], "target_candidates": [a, b], "decision_relevant_information_lost": True, "observation_validated": False}, {"safe_for_all_source_candidates": True}, "SAFE_CONSUME"),
        ("lossless unique unauthorized", {"source_candidates": [u], "target_candidates": [u], "decision_relevant_information_lost": False, "observation_validated": False}, {"safe_for_all_source_candidates": False}, "UNAUTHORIZED"),
    ]

    for label, transfer, action, expected in cases:
        got = consume(transfer, action)
        assert got == expected, f"{label}: expected {expected}, got {got}"

    print("LOSSY SEMANTIC TRANSFER: 8/8 PASS")


if __name__ == "__main__":
    main()
