import argparse
from pathlib import Path

import pandas as pd
from scipy.stats import mannwhitneyu


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = BASE_DIR / "data" / "external" / "ab_test_results.csv"
DEFAULT_OUTPUT = BASE_DIR / "data" / "processed" / "ab_test_results_summary.csv"
REQUIRED_COLUMNS = {"experiment_id", "variant", "metric_value"}


def analyze_ab_tests(results: pd.DataFrame, alpha: float = 0.05) -> pd.DataFrame:
    """Compare two randomized variants for each experiment and metric."""
    missing_columns = REQUIRED_COLUMNS.difference(results.columns)
    if missing_columns:
        raise ValueError(
            f"A/B results are missing required columns: {', '.join(sorted(missing_columns))}"
        )
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")

    results = results.copy()
    results["metric_value"] = pd.to_numeric(results["metric_value"], errors="coerce")
    results = results.dropna(subset=["experiment_id", "variant", "metric_value"])
    if results.empty:
        raise ValueError("A/B results contain no valid observations")

    if "metric_name" not in results.columns:
        results["metric_name"] = "metric_value"

    summaries = []
    for (experiment_id, metric_name), group in results.groupby(
        ["experiment_id", "metric_name"]
    ):
        variants = sorted(group["variant"].unique())
        if len(variants) != 2:
            raise ValueError(
                f"Experiment {experiment_id} must contain exactly two variants"
            )

        first = group.loc[group["variant"] == variants[0], "metric_value"]
        second = group.loc[group["variant"] == variants[1], "metric_value"]
        if len(first) < 2 or len(second) < 2:
            raise ValueError(
                f"Experiment {experiment_id} needs at least two observations per variant"
            )

        test = mannwhitneyu(first, second, alternative="two-sided")
        first_mean = first.mean()
        second_mean = second.mean()
        effect = second_mean - first_mean
        relative_effect = (effect / first_mean) * 100 if first_mean else float("nan")
        winner = variants[1] if effect > 0 else variants[0]

        summaries.append(
            {
                "experiment_id": experiment_id,
                "metric_name": metric_name,
                "variant_a": variants[0],
                "variant_b": variants[1],
                "variant_a_count": len(first),
                "variant_b_count": len(second),
                "variant_a_mean": first_mean,
                "variant_b_mean": second_mean,
                "absolute_effect_b_minus_a": effect,
                "relative_effect_pct": relative_effect,
                "winner_by_mean": winner,
                "mannwhitney_u": test.statistic,
                "p_value": test.pvalue,
                "statistically_significant": test.pvalue < alpha,
                "interpretation": (
                    "Evidence of a difference within this experiment."
                    if test.pvalue < alpha
                    else "No statistically significant difference detected."
                ),
            }
        )

    return pd.DataFrame(summaries)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--alpha", type=float, default=0.05)
    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError(
            f"A/B results not found: {args.input}. "
            "Collect controlled experiment data before running this analysis."
        )

    summary = analyze_ab_tests(pd.read_csv(args.input), alpha=args.alpha)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(args.output, index=False)
    print(summary.to_string(index=False))
    print(f"\nA/B test summary saved to: {args.output}")


if __name__ == "__main__":
    main()