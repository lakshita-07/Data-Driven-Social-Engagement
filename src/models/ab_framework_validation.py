"""Validate the A/B analysis framework against synthetic known effects."""

from pathlib import Path

import numpy as np
import pandas as pd

from src.models.ab_testing import analyze_ab_tests


ROOT = Path(__file__).resolve().parents[2]
OUTPUT = ROOT / "data" / "processed" / "ab_framework_validation.csv"


def simulate(effect: float, n: int = 60, seed: int = 0) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    first = rng.normal(5.0, 1.5, n)
    second = rng.normal(5.0 + effect, 1.5, n)
    return pd.DataFrame(
        {
            "experiment_id": "synthetic_validation",
            "variant": ["A"] * n + ["B"] * n,
            "metric_name": "engagement_rate",
            "metric_value": np.r_[first, second],
        }
    )


def validate(
    effects=(0.0, 0.25, 0.5, 1.0, 1.5),
    seeds=range(100),
    alpha: float = 0.05,
) -> pd.DataFrame:
    rows = []
    for effect in effects:
        significant = 0
        for seed in seeds:
            summary = analyze_ab_tests(simulate(effect, seed=seed), alpha=alpha)
            significant += int(summary.loc[0, "statistically_significant"])
        rows.append(
            {
                "effect_size": effect,
                "simulations": len(seeds),
                "significant_results": significant,
                "detection_rate": significant / len(seeds),
                "alpha": alpha,
            }
        )
    return pd.DataFrame(rows)


def main() -> None:
    results = validate()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(OUTPUT, index=False)
    print(results.to_string(index=False))
    print(f"\nValidation results saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
