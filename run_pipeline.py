"""Run the DDSE analytics pipeline in deterministic demo or live mode."""

from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

import pandas as pd

from src.demo_data import generate_demo_inputs
from src.data_collection.youtube_api import collect_videos
from src.data_collection.youtube_comments import collect_comments
from src.database.load_processed import load_processed_outputs
from src.feature_engineering.content_features import calculate_features
from src.feature_engineering.topic_analysis import classify_topic
from src.models.recommendation_engine import build_recommendations
from src.models.statistical_tests import compare_groups
from src.models.topic_relatability import build_topic_relatability
from src.models.trend_forecasting import forecast_keyword_trends
from src.models.virality_analysis import calculate_virality_score, classify_virality
from src.nlp.relatability_analysis import calculate_relatability_score, classify_relatability
from src.nlp.sentiment_analysis import get_polarity, get_sentiment

ROOT = Path(__file__).resolve().parent


def save(dataframe: pd.DataFrame, directory: Path, filename: str) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(directory / filename, index=False)


def preprocess_raw(
    posts_path: Path | pd.DataFrame,
    comments_path: Path | pd.DataFrame,
    processed: Path,
) -> None:
    posts = posts_path.copy() if isinstance(posts_path, pd.DataFrame) else pd.read_csv(posts_path)
    comments = (
        comments_path.copy()
        if isinstance(comments_path, pd.DataFrame)
        else pd.read_csv(comments_path)
    )
    posts["posting_datetime"] = pd.to_datetime(posts["posting_datetime"], errors="coerce")
    posts = posts.drop_duplicates("post_id").reset_index(drop=True)
    for column in ("duration_seconds", "views", "likes", "comments_count"):
        posts[column] = pd.to_numeric(posts[column], errors="coerce").clip(lower=0).fillna(0)
    posts["caption"] = posts["caption"].fillna("")
    posts["hashtags"] = posts["hashtags"].fillna("")
    comments = comments.drop_duplicates("comment_id").copy()
    comments["comment_text"] = comments["comment_text"].fillna("").astype(str)
    comments["cleaned_text"] = (
        comments["comment_text"].str.lower()
        .str.replace(r"http\S+|www\S+", "", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    comments = comments[comments["cleaned_text"].ne("")].reset_index(drop=True)
    save(posts, processed, "posts_processed.csv")
    save(comments, processed, "comments_processed.csv")


def preprocess_public_youtube_raw(raw: Path, processed: Path) -> None:
    """Adapt the exact public API raw schemas to the existing analysis schema."""
    videos = pd.read_csv(raw / "youtube_videos_raw.csv")
    comments = pd.read_csv(raw / "youtube_comments_raw.csv")
    videos = videos.rename(
        columns={
            "video_id": "post_id",
            "channel_id": "account_id",
            "duration_sec": "duration_seconds",
            "published_at": "posting_datetime",
            "tags": "hashtags",
        }
    )
    videos["platform"] = "YouTube"
    videos["content_type"] = videos["duration_seconds"].apply(
        lambda value: "Short" if pd.notna(value) and value <= 60 else "Long-form"
    )
    videos["caption"] = (
        videos["title"].fillna("") + "\n\n" + videos["description"].fillna("")
    ).str.strip()
    for column in ("shares", "saves", "retention_rate"):
        videos[column] = pd.NA
    comments = comments.rename(
        columns={
            "video_id": "post_id",
            "comment_published_at": "comment_datetime",
        }
    )
    preprocess_raw(
        videos[
            [
                "post_id", "platform", "account_id", "content_type", "caption",
                "hashtags", "posting_datetime", "duration_seconds", "views",
                "likes", "comments_count", "shares", "saves", "retention_rate",
            ]
        ],
        comments[["comment_id", "post_id", "comment_text", "comment_datetime"]],
        processed,
    )


def run_analysis(processed: Path, trend_input: Optional[Path] = None) -> List[str]:
    posts = calculate_features(pd.read_csv(processed / "posts_processed.csv"))
    save(posts, processed, "posts_features.csv")
    posts = calculate_virality_score(posts)
    low, high = posts["virality_score"].quantile([0.33, 0.66])
    posts["virality_level"] = posts["virality_score"].apply(
        classify_virality, args=(low, high)
    )
    save(posts, processed, "posts_virality.csv")

    comments = pd.read_csv(processed / "comments_processed.csv")
    comments["polarity"] = comments["cleaned_text"].fillna("").apply(get_polarity)
    comments["sentiment"] = comments["polarity"].apply(get_sentiment)
    comments["relatability_score"] = comments["cleaned_text"].apply(
        calculate_relatability_score
    )
    comments["relatability"] = comments["relatability_score"].apply(
        classify_relatability
    )
    save(comments, processed, "comments_sentiment.csv")
    save(comments, processed, "comments_relatability.csv")

    posts["topic"] = posts["caption"].fillna("").apply(classify_topic)
    save(posts, processed, "posts_topics.csv")
    topic_performance = (
        posts.groupby("topic", as_index=False)
        .agg(
            video_count=("post_id", "count"),
            average_views=("views", "mean"),
            median_views=("views", "median"),
            average_engagement_rate=("engagement_rate", "mean"),
            median_engagement_rate=("engagement_rate", "median"),
            average_virality_score=("virality_score", "mean"),
            median_virality_score=("virality_score", "median"),
        )
        .sort_values("average_virality_score", ascending=False)
    )
    save(topic_performance, processed, "topic_performance.csv")
    topic_relatability = build_topic_relatability(
        processed / "comments_relatability.csv", processed / "posts_topics.csv"
    )
    save(topic_relatability, processed, "topic_relatability.csv")

    format_analysis = posts.groupby("content_type", as_index=False).agg(
        video_count=("post_id", "count"),
        average_views=("views", "mean"),
        average_likes=("likes", "mean"),
        average_comments=("comments_count", "mean"),
        average_engagement_rate=("engagement_rate", "mean"),
        average_virality_score=("virality_score", "mean"),
    )
    save(format_analysis, processed, "format_analysis.csv")
    for column, filename in (
        ("posting_hour", "hourly_analysis.csv"),
        ("posting_day", "day_analysis.csv"),
    ):
        summary = posts.groupby(column, as_index=False).agg(
            video_count=("post_id", "count"),
            average_views=("views", "mean"),
            median_views=("views", "median"),
            average_engagement_rate=("engagement_rate", "mean"),
            median_engagement_rate=("engagement_rate", "median"),
        )
        save(summary, processed, filename)

    comparisons = pd.DataFrame(
        [
            compare_groups(posts, column)
            for column in (
                "content_type",
                "video_length_group",
                "posting_hour",
                "posting_day",
            )
        ]
    )
    save(comparisons, processed, "historical_statistical_tests.csv")
    recommendations = build_recommendations(
        processed / "posts_topics.csv", processed / "topic_relatability.csv"
    )
    save(recommendations, processed, "recommendations.csv")

    warnings = []
    if trend_input and trend_input.exists():
        forecasts = forecast_keyword_trends(pd.read_csv(trend_input))
        save(forecasts, processed, "trend_forecasts.csv")
    else:
        warnings.append("External trend data not connected")
    return warnings


def write_manifest(mode: str, raw: Path, processed: Path, warnings: List[str]) -> None:
    counts = {
        path.name: len(pd.read_csv(path))
        for path in sorted(processed.glob("*.csv"))
    }
    manifest = {
        "mode": mode,
        "source": (
            "fixed-seed synthetic demo inputs"
            if mode == "demo"
            else "YouTube API and configured database"
        ),
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "schema_version": "1.0",
        "raw_directory": str(raw.relative_to(ROOT)),
        "processed_directory": str(processed.relative_to(ROOT)),
        "row_counts": counts,
        "warnings": warnings,
    }
    processed.mkdir(parents=True, exist_ok=True)
    (processed / "dataset_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )


def run_demo() -> None:
    raw = ROOT / "data" / "raw" / "demo"
    processed = ROOT / "data" / "processed" / "demo"
    posts, comments, trends = generate_demo_inputs(raw)
    preprocess_raw(posts, comments, processed)
    warnings = run_analysis(processed, trends)
    write_manifest("demo", raw, processed, warnings)
    print(f"Demo pipeline completed: {processed}")


def run_live(
    collect: bool,
    max_videos: int,
    max_comments_per_video: int,
    use_database: bool,
) -> None:
    raw = ROOT / "data" / "raw"
    if collect:
        collect_videos(max_videos=max_videos, output=raw / "youtube_videos_raw.csv")
        collect_comments(
            max_comments_per_video=max_comments_per_video,
            input=raw / "youtube_videos_raw.csv",
            output=raw / "youtube_comments_raw.csv",
        )
    posts_path = raw / "youtube_videos_raw.csv"
    comments_path = raw / "youtube_comments_raw.csv"
    missing = [str(path) for path in (posts_path, comments_path) if not path.exists()]
    if missing:
        raise RuntimeError(
            "Live mode requires raw CSV files. Missing: " + ", ".join(missing)
        )
    videos = pd.read_csv(posts_path)
    if videos.empty:
        raise RuntimeError(
            "Live collection produced no videos; processed outputs were not regenerated."
        )
    processed = ROOT / "data" / "processed"
    preprocess_public_youtube_raw(raw, processed)
    warnings = run_analysis(processed)
    write_manifest("live", raw, processed, warnings)
    if use_database:
        load_processed_outputs(processed)
    print(f"Live pipeline completed: {processed}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("demo", "live"), default="demo")
    collection = parser.add_mutually_exclusive_group()
    collection.add_argument("--collect", action="store_true")
    collection.add_argument("--skip-collect", action="store_true")
    parser.add_argument("--max-videos", type=int, default=100)
    parser.add_argument("--max-comments-per-video", type=int, default=100)
    parser.add_argument(
        "--use-database",
        action="store_true",
        help="Load processed posts and comments into configured MySQL tables",
    )
    args = parser.parse_args()
    if args.mode == "demo":
        run_demo()
    else:
        run_live(
            collect=args.collect,
            max_videos=args.max_videos,
            max_comments_per_video=args.max_comments_per_video,
            use_database=args.use_database,
        )


if __name__ == "__main__":
    main()
