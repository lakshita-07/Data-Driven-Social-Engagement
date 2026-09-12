"""Generate deterministic synthetic inputs for the DDSE demo mode."""

from pathlib import Path

import numpy as np
import pandas as pd


def generate_demo_inputs(raw_dir: Path, seed: int = 42) -> tuple[Path, Path, Path]:
    rng = np.random.default_rng(seed)
    raw_dir.mkdir(parents=True, exist_ok=True)
    dates = pd.date_range("2025-01-06", periods=24, freq="7D")
    topics = [
        "Academic Pressure",
        "Procrastination and Productivity",
        "Career and Job Anxiety",
        "Burnout and Mental Pressure",
    ]
    rows = []
    comment_rows = []
    for index in range(48):
        topic = topics[index % len(topics)]
        post_id = f"demo-video-{index + 1:03d}"
        posted = dates[index % len(dates)] + pd.Timedelta(hours=12 + index % 8)
        views = int(rng.integers(20_000, 2_000_000))
        likes = int(views * rng.uniform(0.01, 0.09))
        comments = int(views * rng.uniform(0.001, 0.02))
        duration = int(rng.integers(15, 180))
        rows.append(
            {
                "post_id": post_id,
                "platform": "YouTube",
                "account_id": "demo-channel",
                "content_type": "Short" if duration <= 60 else "Long-form",
                "caption": f"{topic}: practical ideas for everyday life",
                "hashtags": f"#{topic.split()[0].lower()} #demo",
                "posting_datetime": posted.isoformat(),
                "duration_seconds": duration,
                "views": views,
                "likes": likes,
                "comments_count": comments,
                "shares": np.nan,
                "saves": np.nan,
                "retention_rate": np.nan,
            }
        )
        for comment_index in range(8):
            relatable = comment_index % 3 == 0
            text = (
                f"This is literally me dealing with {topic.lower()}"
                if relatable
                else "Very useful video, thank you"
            )
            comment_rows.append(
                {
                    "comment_id": f"demo-comment-{index + 1:03d}-{comment_index + 1:02d}",
                    "post_id": post_id,
                    "comment_text": text,
                    "comment_datetime": posted + pd.Timedelta(hours=2),
                }
            )

    posts = pd.DataFrame(rows)
    comments = pd.DataFrame(comment_rows)
    keywords = []
    for keyword, base in (("burnout", 100), ("procrastination", 140), ("study stress", 110)):
        for index, date in enumerate(pd.date_range("2025-01-05", periods=12, freq="7D")):
            keywords.append({"keyword": keyword, "date": date, "volume": base + index * 8 + int(rng.integers(0, 10))})
    keyword_history = pd.DataFrame(keywords)

    posts_path = raw_dir / "youtube_posts_raw.csv"
    comments_path = raw_dir / "youtube_comments_raw.csv"
    trends_path = raw_dir / "keyword_history_demo.csv"
    posts.to_csv(posts_path, index=False)
    comments.to_csv(comments_path, index=False)
    keyword_history.to_csv(trends_path, index=False)
    return posts_path, comments_path, trends_path
