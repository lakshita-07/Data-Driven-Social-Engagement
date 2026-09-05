from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
POSTS_PATH = BASE_DIR / "data" / "processed" / "posts_topics.csv"
RELATABILITY_PATH = BASE_DIR / "data" / "processed" / "topic_relatability.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "recommendations.csv"


def percentile_score(series: pd.Series) -> pd.Series:
    if series.nunique() <= 1:
        return pd.Series(1.0, index=series.index)
    return series.rank(method="average", pct=True)


def add_rank_score(
    summary: pd.DataFrame,
    metric_weights: dict[str, float],
) -> pd.DataFrame:
    summary = summary.copy()
    summary["recommendation_score"] = 0.0
    for metric, weight in metric_weights.items():
        summary["recommendation_score"] += percentile_score(summary[metric]) * weight
    return summary.sort_values("recommendation_score", ascending=False)


def build_recommendations(
    posts_path: Path = POSTS_PATH,
    relatability_path: Path = RELATABILITY_PATH,
) -> pd.DataFrame:
    posts = pd.read_csv(posts_path)
    topic_relatability = pd.read_csv(relatability_path)

    posts["posting_datetime"] = pd.to_datetime(posts["posting_datetime"], errors="coerce")
    posts["posting_hour"] = posts["posting_datetime"].dt.hour
    posts["posting_day"] = posts["posting_datetime"].dt.day_name()

    topic_summary = (
        posts.groupby("topic", as_index=False)
        .agg(
            video_count=("post_id", "nunique"),
            average_engagement_rate=("engagement_rate", "mean"),
            average_virality_score=("virality_score", "mean"),
        )
        .merge(topic_relatability, on="topic", how="left", validate="one_to_one")
    )
    topic_summary = add_rank_score(
        topic_summary,
        {
            "average_engagement_rate": 0.40,
            "average_virality_score": 0.35,
            "relatable_comment_rate": 0.25,
        },
    )
    topic_summary["recommendation_type"] = "Topic"
    topic_summary["recommendation"] = topic_summary["topic"]
    topic_summary["evidence_note"] = topic_summary["video_count"].map(
        lambda count: "Descriptive result; review cautiously because fewer than 10 videos were observed."
        if count < 10
        else "Descriptive historical result; not evidence of causation."
    )

    format_summary = (
        posts.groupby("content_type", as_index=False)
        .agg(
            video_count=("post_id", "nunique"),
            average_engagement_rate=("engagement_rate", "mean"),
            average_virality_score=("virality_score", "mean"),
        )
    )
    format_summary["comment_count"] = pd.NA
    format_summary["relatable_comment_count"] = pd.NA
    format_summary["relatable_comment_rate"] = pd.NA
    format_summary = add_rank_score(
        format_summary,
        {"average_engagement_rate": 0.55, "average_virality_score": 0.45},
    )
    format_summary["recommendation_type"] = "Format"
    format_summary["recommendation"] = format_summary["content_type"]
    format_summary["evidence_note"] = "Observational comparison; not a randomized A/B test."

    recommendation_frames = [topic_summary, format_summary]
    for column, label in (("posting_hour", "Posting hour"), ("posting_day", "Posting day")):
        time_summary = (
            posts.groupby(column, as_index=False)
            .agg(
                video_count=("post_id", "nunique"),
                average_engagement_rate=("engagement_rate", "mean"),
                average_virality_score=("virality_score", "mean"),
            )
        )
        time_summary["comment_count"] = pd.NA
        time_summary["relatable_comment_count"] = pd.NA
        time_summary["relatable_comment_rate"] = pd.NA
        time_summary = add_rank_score(
            time_summary,
            {"average_engagement_rate": 0.55, "average_virality_score": 0.45},
        )
        time_summary["recommendation_type"] = label
        time_summary["recommendation"] = time_summary[column].astype(str)
        time_summary["evidence_note"] = "Historical observation; current tests found no statistically significant timing effect."
        recommendation_frames.append(time_summary)

    columns = [
        "recommendation_type",
        "recommendation",
        "video_count",
        "comment_count",
        "relatable_comment_count",
        "relatable_comment_rate",
        "average_engagement_rate",
        "average_virality_score",
        "recommendation_score",
        "evidence_note",
    ]
    return pd.concat(recommendation_frames, ignore_index=True)[columns]


def main() -> None:
    recommendations = build_recommendations()
    recommendations.to_csv(OUTPUT_PATH, index=False)
    print(recommendations.to_string(index=False))
    print(f"\nRecommendations saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()