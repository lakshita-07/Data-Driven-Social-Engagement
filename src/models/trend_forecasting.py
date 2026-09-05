import argparse
from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = BASE_DIR / "data" / "external" / "keyword_history.csv"
DEFAULT_OUTPUT = BASE_DIR / "data" / "processed" / "trend_forecasts.csv"
REQUIRED_COLUMNS = {"keyword", "date", "volume"}


def forecast_keyword_trends(history: pd.DataFrame) -> pd.DataFrame:
    """Estimate keyword direction from dated external search-volume observations."""
    missing_columns = REQUIRED_COLUMNS.difference(history.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"Trend history is missing required columns: {missing}")

    history = history.copy()
    history["date"] = pd.to_datetime(history["date"], errors="coerce")
    history["volume"] = pd.to_numeric(history["volume"], errors="coerce")
    history = history.dropna(subset=["keyword", "date", "volume"])
    if history.empty:
        raise ValueError("Trend history has no valid keyword, date, and volume rows")

    forecasts = []
    for keyword, group in history.groupby("keyword"):
        daily = (
            group.groupby("date", as_index=False)["volume"]
            .mean()
            .sort_values("date")
            .reset_index(drop=True)
        )
        if len(daily) < 3:
            continue

        window = max(1, len(daily) // 3)
        recent = daily.tail(window)["volume"]
        previous = daily.iloc[-2 * window : -window]["volume"]
        previous_average = previous.mean()
        recent_average = recent.mean()
        growth_rate = (
            ((recent_average - previous_average) / previous_average) * 100
            if previous_average
            else np.nan
        )
        slope = np.polyfit(np.arange(len(daily)), daily["volume"], 1)[0]

        if pd.notna(growth_rate) and growth_rate >= 10 and slope > 0:
            trend = "Rising"
        elif pd.notna(growth_rate) and growth_rate <= -10 and slope < 0:
            trend = "Declining"
        else:
            trend = "Stable"

        forecasts.append(
            {
                "keyword": keyword,
                "latest_date": daily["date"].iloc[-1],
                "data_points": len(daily),
                "recent_average_volume": recent_average,
                "previous_average_volume": previous_average,
                "growth_rate_pct": growth_rate,
                "trend_slope": slope,
                "trend": trend,
            }
        )

    if not forecasts:
        raise ValueError("No keyword has at least three dated observations")

    return pd.DataFrame(forecasts).sort_values(
        ["trend", "growth_rate_pct"], ascending=[True, False]
    ).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if not args.input.exists():
        raise FileNotFoundError(
            f"External trend history not found: {args.input}. "
            "Create a CSV with keyword,date,volume columns first."
        )

    forecasts = forecast_keyword_trends(pd.read_csv(args.input))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    forecasts.to_csv(args.output, index=False)
    print(forecasts.to_string(index=False))
    print(f"\nTrend forecasts saved to: {args.output}")


if __name__ == "__main__":
    main()