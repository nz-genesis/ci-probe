"""Executable checks for the differential realization experiment."""

from differential_realization import run_differential


def test_two_mechanisms_satisfy_one_contract() -> None:
    direct, queued = run_differential()
    assert direct.outcome == queued.outcome == "applied"
    assert direct.observed_value == queued.observed_value == "v1"


def test_evidence_retains_mechanism_provenance() -> None:
    direct, queued = run_differential()
    assert direct.mechanism == "direct"
    assert queued.mechanism == "queued"


if __name__ == "__main__":
    test_two_mechanisms_satisfy_one_contract()
    test_evidence_retains_mechanism_provenance()
    print("differential realization: PASS")
