"""Total-cost measurement protocol self-test.

This is a measurement harness, not evidence that any strategy is cheaper.
It enforces that quality/safety gates are hard constraints and keeps resource
metrics separate so an arbitrary scalar score cannot hide regressions.
"""
from dataclasses import dataclass
from math import isfinite
from typing import Iterable

DIMENSIONS = (
    "tokens",
    "api_calls",
    "wall_time_ms",
    "cpu_ms",
    "memory_mb_peak",
    "energy_proxy",
    "verification_cost",
    "recovery_cost",
    "human_attention_units",
    "complexity_units",
    "risk_units",
    "opportunity_cost_units",
    "downstream_loss_units",
)

@dataclass(frozen=True)
class Trial:
    strategy: str
    quality: float
    safety: float
    dimensions: dict[str, float]

REQUIRED_QUALITY = 0.90
REQUIRED_SAFETY = 1.00


def validate_trial(t: Trial) -> None:
    assert isfinite(t.quality) and isfinite(t.safety)
    assert 0.0 <= t.quality <= 1.0
    assert 0.0 <= t.safety <= 1.0
    assert set(t.dimensions) == set(DIMENSIONS), (t.strategy, set(t.dimensions) ^ set(DIMENSIONS))
    assert all(isfinite(v) and v >= 0.0 for v in t.dimensions.values()), t.strategy


def eligible(t: Trial) -> bool:
    return t.quality >= REQUIRED_QUALITY and t.safety >= REQUIRED_SAFETY


def pareto_frontier(trials: Iterable[Trial]) -> list[str]:
    xs=list(trials)
    for t in xs: validate_trial(t)
    good=[t for t in xs if eligible(t)]
    names=[]
    for t in good:
        dominated=False
        for u in good:
            if u is t: continue
            no_worse=all(u.dimensions[d] <= t.dimensions[d] for d in DIMENSIONS)
            strictly_better=any(u.dimensions[d] < t.dimensions[d] for d in DIMENSIONS)
            if no_worse and strictly_better:
                dominated=True; break
        if not dominated: names.append(t.strategy)
    return names


def self_test() -> None:
    base={d:100.0 for d in DIMENSIONS}
    trials=[
        Trial("A_max_verification",1.0,1.0,{**base,"tokens":180,"api_calls":6,"verification_cost":90,"wall_time_ms":240}),
        Trial("B_selective_verification",0.96,1.0,{**base,"tokens":125,"api_calls":4,"verification_cost":55,"wall_time_ms":170}),
        Trial("C_cached_cognition_revalidate",0.95,1.0,{**base,"tokens":70,"api_calls":3,"verification_cost":60,"wall_time_ms":120,"human_attention_units":45}),
        Trial("D_optional_envelope",0.95,1.0,{**base,"tokens":72,"api_calls":3,"verification_cost":52,"wall_time_ms":118,"complexity_units":110}),
        Trial("unsafe_cheap",0.99,0.80,{**base,"tokens":20,"api_calls":1}),
    ]
    assert pareto_frontier(trials)
    assert "unsafe_cheap" not in pareto_frontier(trials)
    assert len(pareto_frontier(trials)) >= 1
    print("measurement_protocol_self_test=PASS")
    print("hard_quality_gate=0.90")
    print("hard_safety_gate=1.00")
    print("eligible_frontier="+",".join(pareto_frontier(trials)))
    print("empirical_strategy_winner=NOT_DETERMINED")

if __name__ == "__main__": self_test()
