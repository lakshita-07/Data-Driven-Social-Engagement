"""Collect public top-level YouTube comments for locally stored videos."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_COLUMNS = [
    "comment_id",
    "video_id",
    "comment_text",
    "comment_like_count",
    "comment_published_at",
    "author_channel_id",
    "source_type",
]


def get_youtube_service(api_key: str | None = None):
    load_dotenv()
    key = api_key or os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY is required for public YouTube collection")
    return build("youtube", "v3", developerKey=key)


def _api_reason(error: Exception) -> str:
    if isinstance(error, HttpError):
        return str(error).lower()
    return str(error).lower()


def save_rows(rows: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=RAW_COLUMNS).to_csv(output, index=False)


def get_video_ids(input_path: Path) -> list[str]:
    videos = pd.read_csv(input_path)
    if "video_id" not in videos.columns:
        raise ValueError(f"Input does not contain required video_id column: {input_path}")
    return videos["video_id"].dropna().astype(str).drop_duplicates().tolist()


def collect_comments_for_video(
    youtube, video_id: str, max_comments: int
) -> list[dict[str, Any]]:
    comments: list[dict[str, Any]] = []
    request = youtube.commentThreads().list(
        part="snippet", videoId=video_id, maxResults=min(max_comments, 100),
        textFormat="plainText",
    )
    while request and len(comments) < max_comments:
        response = request.execute()
        for item in response.get("items", []):
            top_level = item.get("snippet", {}).get("topLevelComment", {})
            snippet = top_level.get("snippet", {})
            comments.append(
                {
                    "comment_id": top_level.get("id"),
                    "video_id": video_id,
                    "comment_text": snippet.get("textDisplay", ""),
                    "comment_like_count": snippet.get("likeCount"),
                    "comment_published_at": snippet.get("publishedAt"),
                    "author_channel_id": (snippet.get("authorChannelId") or {}).get(
                        "value"
                    ),
                    "source_type": "public_youtube_api",
                }
            )
            if len(comments) >= max_comments:
                break
        next_page = response.get("nextPageToken")
        request = (
            youtube.commentThreads().list(
                part="snippet", videoId=video_id,
                maxResults=min(max_comments - len(comments), 100),
                pageToken=next_page, textFormat="plainText",
            )
            if next_page and len(comments) < max_comments
            else None
        )
    return comments


def collect_comments(
    max_comments_per_video: int = 100,
    input: str | Path | None = None,
    output: str | Path | None = None,
    youtube=None,
) -> Path:
    load_dotenv()
    input_path = Path(input) if input else PROJECT_ROOT / "data/raw/youtube_videos_raw.csv"
    output_path = Path(output) if output else PROJECT_ROOT / "data/raw/youtube_comments_raw.csv"
    if not input_path.is_absolute():
        input_path = PROJECT_ROOT / input_path
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path
    max_comments_per_video = max(0, max_comments_per_video)
    rows: list[dict[str, Any]] = []
    save_rows(rows, output_path)

    try:
        youtube = youtube or get_youtube_service()
        video_ids = get_video_ids(input_path)
        print(f"Videos found: {len(video_ids)}")
        for index, video_id in enumerate(video_ids, start=1):
            try:
                comments = collect_comments_for_video(
                    youtube, video_id, max_comments_per_video
                )
                rows.extend(comments)
                print(
                    f"Video {index}/{len(video_ids)} {video_id}: "
                    f"{len(comments)} comments"
                )
            except Exception as error:
                reason = _api_reason(error)
                if "commentsdisabled" in reason or "videonotfound" in reason:
                    print(f"Skipping {video_id}: comments unavailable or video not found")
                else:
                    print(f"Could not collect comments for {video_id}: {error}")
            save_rows(rows, output_path)
    except Exception as error:
        print(f"Comment collection stopped: {error}")
    finally:
        save_rows(rows, output_path)

    print(f"Comment collection completed. Total comments collected: {len(rows)}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--max_comments_per_video", type=int, default=100)
    parser.add_argument("--input", default=None)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    collect_comments(**vars(args))


if __name__ == "__main__":
    main()
