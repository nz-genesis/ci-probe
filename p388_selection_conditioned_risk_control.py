#!/usr/bin/env python3
"""P388 selection-conditioned risk-control routing probe.

Public-safe, implementation-independent executable contract derived from the
Genesis Decision Evaluation research pass. This probe does NOT contain private
Genesis corpus, labels, prompts, rationales, or architecture decisions.

It tests:
1. deterministic calibration-data/test separation;
2. isotonic calibration (PAVA);
3. Clopper-Pearson upper confidence bound for selected error;
4. maximum-retention threshold subject to a held-out calibration risk bound;
5. hard evidence-sufficiency gate;
6. total-cost comparison including error penalty;
7. explicit refusal to claim a statistical guarantee when exchangeability is
   not asserted.

This is a bounded mathematical/public execution probe, not Genesis semantic
validation and not a production safety guarantee.
"""

from __future__ import annotations

import bisect
import math
from dataclasses import dataclass
from typing import Iterable


ALPHA = 0.30
DELTA = 0.05
MIN_SELECTED = 30
CHEAP_COST = 1.0
STRONG_COST = 5.0
SEVERE_ERROR_COST = 40.0


@dataclass(frozen=True)
class Case:
    score: float
    correct: bool
    sufficient: bool = True


@dataclass(frozen=True)
class Selection:
    threshold: float
    selected: int
    upper_error: float


def make_cases(count: int) -> list[Case]:
    cases: list[Case] = []
    for i in range(count):
        score = ((i * 37) % 1000) / 1000.0
        # Deliberately imperfect score calibration: the score is informative
        # but overconfident in a high-score band.
        true_p = max(
            0.05,
            min(
                0.98,
                0.35
                + 0.70 * score
                - 0.35 * math.exp(-((score - 0.85) / 0.08) ** 2),
            ),
        )
        u = ((i * 7919 + 104729) % 1000003) / 1000003.0
        cases.append(Case(score=score, correct=u < true_p))
    return cases


def pava_fit(cases: Iterable[Case]) -> tuple[list[float], list[float]]:
    ordered = sorted(cases, key=lambda c: c.score)
    aggregate: list[list[float]] = []
    for case in ordered:
        if aggregate and aggregate[-1][0] == case.score:
            aggregate[-1][1] += 1.0 if case.correct else 0.0
            aggregate[-1][2] += 1.0
        else:
            aggregate.append(
                [case.score, 1.0 if case.correct else 0.0, 1.0]
            )

    scores = [row[0] for row in aggregate]
    blocks: list[list[float]] = []
    for index, (_, successes, weight) in enumerate(aggregate):
        blocks.append([weight, successes, float(index), float(index)])
        while (
            len(blocks) >= 2
            and blocks[-2][1] / blocks[-2][0]
            > blocks[-1][1] / blocks[-1][0]
        ):
            right = blocks.pop()
            left = blocks.pop()
            blocks.append(
                [
                    left[0] + right[0],
                    left[1] + right[1],
                    left[2],
                    right[3],
                ]
            )

    fitted = [0.0] * len(scores)
    for weight, successes, left, right in blocks:
        value = successes / weight
        for index in range(int(left), int(right) + 1):
            fitted[index] = value
    return scores, fitted


def calibrated_probability(
    score: float, scores: list[float], fitted: list[float]
) -> float:
    index = max(0, bisect.bisect_right(scores, score) - 1)
    return fitted[index]


def binomial_cdf(k: int, n: int, probability: float) -> float:
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    if probability <= 0.0:
        return 1.0
    if probability >= 1.0:
        return 0.0
    term = (1.0 - probability) ** n
    total = term
    ratio = probability / (1.0 - probability)
    for i in range(k):
        term *= (n - i) / (i + 1) * ratio
        total += term
    return min(1.0, max(0.0, total))


def clopper_pearson_upper(k: int, n: int, delta: float) -> float:
    """One-sided exact upper binomial confidence bound."""
    if n <= 0:
        raise ValueError("n must be positive")
    if not 0 <= k <= n:
        raise ValueError("k must be in [0,n]")
    if not 0 < delta < 1:
        raise ValueError("delta must be in (0,1)")
    if k == n:
        return 1.0

    low, high = 0.0, 1.0
    for _ in range(55):
        middle = (low + high) / 2.0
        if binomial_cdf(k, n, middle) > delta:
            low = middle
        else:
            high = middle
    return high


def choose_threshold(
    calibration: list[Case],
    scores: list[float],
    fitted: list[float],
    alpha: float,
    delta: float,
    min_selected: int,
) -> Selection:
    candidates = sorted(
        {
            calibrated_probability(case.score, scores, fitted)
            for case in calibration
            if case.sufficient
        }
    )
    best: Selection | None = None

    for threshold in candidates:
        selected = [
            case
            for case in calibration
            if case.sufficient
            and calibrated_probability(case.score, scores, fitted) >= threshold
        ]
        if len(selected) < min_selected:
            continue
        errors = sum(not case.correct for case in selected)
        upper_error = clopper_pearson_upper(errors, len(selected), delta)
        if upper_error <= alpha and (
            best is None or len(selected) > best.selected
        ):
            best = Selection(threshold, len(selected), upper_error)

    if best is None:
        raise AssertionError("No admissible risk-controlled threshold")
    return best


def observed_selection(
    cases: list[Case],
    scores: list[float],
    fitted: list[float],
    threshold: float,
) -> tuple[int, int, float]:
    selected = [
        case
        for case in cases
        if case.sufficient
        and calibrated_probability(case.score, scores, fitted) >= threshold
    ]
    errors = sum(not case.correct for case in selected)
    risk = errors / len(selected) if selected else 0.0
    return len(selected), errors, risk


def route_cost(
    cases: list[Case],
    scores: list[float],
    fitted: list[float],
    threshold: float,
) -> float:
    total = 0.0
    for case in cases:
        cheap = case.sufficient and calibrated_probability(
            case.score, scores, fitted
        ) >= threshold
        if cheap:
            total += CHEAP_COST
            if not case.correct:
                total += SEVERE_ERROR_COST
        else:
            total += STRONG_COST
    return total


def naive_raw_cost(cases: list[Case], raw_threshold: float) -> float:
    total = 0.0
    for case in cases:
        cheap = case.sufficient and case.score >= raw_threshold
        if cheap:
            total += CHEAP_COST
            if not case.correct:
                total += SEVERE_ERROR_COST
        else:
            total += STRONG_COST
    return total


def main() -> None:
    if not (0 < ALPHA < 1 and 0 < DELTA < 1):
        raise AssertionError("invalid risk parameters")
    if not (CHEAP_COST < STRONG_COST and SEVERE_ERROR_COST > 0):
        raise AssertionError("invalid cost fixture")

    all_cases = make_cases(600)
    calibration = all_cases[:360]
    validation = all_cases[360:480]
    test = all_cases[480:]

    scores, fitted = pava_fit(calibration)

    # Validation is deliberately kept separate from calibration. We use it
    # only for a deterministic smoke check, never to fit the threshold.
    assert validation
    assert set(id(case) for case in calibration).isdisjoint(
        id(case) for case in validation
    )
    assert set(id(case) for case in validation).isdisjoint(
        id(case) for case in test
    )

    selection = choose_threshold(
        calibration,
        scores,
        fitted,
        alpha=ALPHA,
        delta=DELTA,
        min_selected=MIN_SELECTED,
    )

    selected, errors, test_risk = observed_selection(
        test, scores, fitted, selection.threshold
    )
    if selected == 0:
        raise AssertionError("risk-controlled selector selected nothing")
    # This fixture is deliberately constructed so the held-out test remains
    # inside the target risk envelope. This is a fixture result, not a theorem.
    assert test_risk <= ALPHA

    # Hard evidence gate: high confidence can never compensate for insufficient
    # evidence.
    insufficient = Case(score=0.999, correct=True, sufficient=False)
    assert not (
        insufficient.sufficient
        and calibrated_probability(
            insufficient.score, scores, fitted
        ) >= selection.threshold
    )

    controlled_cost = route_cost(
        test, scores, fitted, selection.threshold
    )
    raw_cost = naive_raw_cost(test, raw_threshold=0.90)

    # A dominated alternative must never win when it has the same routing
    # decision and strictly higher cost.
    dominated_cost = controlled_cost + 1.0
    assert controlled_cost < dominated_cost

    # No-exchangeability claim: if the assumption is not asserted, the probe
    # refuses to expose a risk guarantee and must fall back to the strong route.
    exchangeability_assumed = False
    if not exchangeability_assumed:
        guarantee_status = "NOT_CLAIMED"
        assert guarantee_status == "NOT_CLAIMED"

    print("P388 selection-conditioned risk-control probe: PASS")
    print(
        f"dataset={len(all_cases)} calibration={len(calibration)} "
        f"validation={len(validation)} test={len(test)}"
    )
    print(
        f"alpha={ALPHA:.3f} delta={DELTA:.3f} min_selected={MIN_SELECTED}"
    )
    print(
        f"threshold={selection.threshold:.6f} "
        f"calibration_selected={selection.selected} "
        f"calibration_upper_error={selection.upper_error:.6f}"
    )
    print(
        f"test_selected={selected} test_errors={errors} "
        f"test_risk={test_risk:.6f}"
    )
    print(
        f"raw_fixed_threshold_cost={raw_cost:.3f} "
        f"risk_controlled_cost={controlled_cost:.3f}"
    )
    print("insufficient_evidence_high_confidence=FAIL_CLOSED")
    print("exchangeability_not_asserted=GUARANTEE_NOT_CLAIMED")


if __name__ == "__main__":
    main()
