from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[2]
COMMENTS_PATH = BASE_DIR / "data" / "processed" / "comments_relatability.csv"
TOPICS_PATH = BASE_DIR / "data" / "processed" / "posts_topics.csv"
OUTPUT_PATH = BASE_DIR / "data" / "processed" / "topic_relatability.csv"


def build_topic_relatability(
    comments_path: Path = COMMENTS_PATH,
    topics_path: Path = TOPICS_PATH,
) -> pd.DataFrame:
    """Join comment classifications to post topics and summarize resonance."""
    comments = pd.read_csv(comments_path)
    posts = pd.read_csv(topics_path, usecols=["post_id", "topic"])

    if posts["post_id"].duplicated().any():
        raise ValueError("posts_topics.csv contains duplicate post_id values")

    joined = comments.merge(posts, on="post_id", how="left", validate="many_to_one")
    unmatched = joined["topic"].isna().sum()
    if unmatched:
        raise ValueError(f"{unmatched} comments could not be assigned a topic")

    joined["is_relatable"] = joined["relatability"].eq("Relatable")

    summary = (
        joined.groupby("topic", as_index=False)
        .agg(
            comment_count=("comment_id", "nunique"),
            relatable_comment_count=("is_relatable", "sum"),
            relatable_comment_rate=("is_relatable", "mean"),
            average_relatability_score=("relatability_score", "mean"),
            average_polarity=("polarity", "mean"),
        )
    )
    summary["relatable_comment_rate"] *= 100
    summary = summary.sort_values(
        ["relatable_comment_rate", "comment_count"],
        ascending=[False, False],
    ).reset_index(drop=True)
    return summary


def main() -> None:
    summary = build_topic_relatability()
    summary.to_csv(OUTPUT_PATH, index=False)
    print(summary.to_string(index=False))
    print(f"\nTopic relatability saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()