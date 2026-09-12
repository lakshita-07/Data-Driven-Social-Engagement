"""Collect public video metadata from a YouTube channel."""

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
    "video_id",
    "channel_id",
    "channel_title",
    "title",
    "description",
    "published_at",
    "duration_iso",
    "duration_sec",
    "views",
    "likes",
    "comments_count",
    "tags",
    "category_id",
    "thumbnail_url",
    "source_type",
]


def duration_to_seconds(duration: str | None) -> int | None:
    """Convert a YouTube ISO 8601 duration to seconds."""
    if not duration or not duration.startswith("PT"):
        return None
    seconds = 0
    number = ""
    for character in duration[2:]:
        if character.isdigit():
            number += character
        elif character in "HMS" and number:
            seconds += int(number) * {"H": 3600, "M": 60, "S": 1}[character]
            number = ""
    return seconds


def get_youtube_service(api_key: str | None = None):
    load_dotenv()
    key = api_key or os.getenv("YOUTUBE_API_KEY")
    if not key:
        raise RuntimeError("YOUTUBE_API_KEY is required for public YouTube collection")
    return build("youtube", "v3", developerKey=key)


def _api_error(error: Exception) -> str:
    if isinstance(error, HttpError):
        return f"YouTube API error ({error.resp.status}): {error}"
    return str(error)


def resolve_channel(youtube, channel_handle: str | None, channel_id: str | None) -> dict[str, Any]:
    """Resolve a handle first, with an explicit channel ID as fallback."""
    if channel_handle:
        try:
            response = youtube.channels().list(
                part="snippet,contentDetails", forHandle=channel_handle.lstrip("@")
            ).execute()
            if response.get("items"):
                return response["items"][0]
            print(f"No channel found for handle {channel_handle}; trying channel ID.")
        except Exception as error:
            print(f"Handle lookup failed for {channel_handle}: {_api_error(error)}")

    if channel_id:
        response = youtube.channels().list(
            part="snippet,contentDetails", id=channel_id
        ).execute()
        if response.get("items"):
            return response["items"][0]

    raise RuntimeError("Could not resolve a YouTube channel from the handle or channel ID")


def _video_row(video: dict[str, Any]) -> dict[str, Any]:
    snippet = video.get("snippet", {})
    details = video.get("contentDetails", {})
    statistics = video.get("statistics", {})
    duration_iso = details.get("duration")

    def count(name: str):
        value = statistics.get(name)
        return int(value) if value is not None else None

    return {
        "video_id": video.get("id"),
        "channel_id": snippet.get("channelId"),
        "channel_title": snippet.get("channelTitle"),
        "title": snippet.get("title"),
        "description": snippet.get("description"),
        "published_at": snippet.get("publishedAt"),
        "duration_iso": duration_iso,
        "duration_sec": duration_to_seconds(duration_iso),
        "views": count("viewCount"),
        "likes": count("likeCount"),
        "comments_count": count("commentCount"),
        "tags": ", ".join(snippet.get("tags", [])),
        "category_id": snippet.get("categoryId"),
        "thumbnail_url": snippet.get("thumbnails", {}).get("high", {}).get("url"),
        "source_type": "public_youtube_api",
    }


def save_rows(rows: list[dict[str, Any]], output: Path) -> None:
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows, columns=RAW_COLUMNS).to_csv(output, index=False)


def collect_videos(
    channel_handle: str | None = None,
    channel_id: str | None = None,
    max_videos: int = 100,
    output: str | Path | None = None,
    youtube=None,
) -> Path:
    load_dotenv()
    channel_handle = channel_handle or os.getenv("YOUTUBE_CHANNEL_HANDLE")
    channel_id = channel_id or os.getenv("YOUTUBE_CHANNEL_ID")
    max_videos = max(0, max_videos)
    output_path = Path(output) if output else PROJECT_ROOT / "data/raw/youtube_videos_raw.csv"
    if not output_path.is_absolute():
        output_path = PROJECT_ROOT / output_path
    rows: list[dict[str, Any]] = []
    save_rows(rows, output_path)

    try:
        youtube = youtube or get_youtube_service()
        channel = resolve_channel(youtube, channel_handle, channel_id)
        uploads_id = channel["contentDetails"]["relatedPlaylists"]["uploads"]
        request = youtube.playlistItems().list(
            part="contentDetails", playlistId=uploads_id, maxResults=min(max_videos, 50)
        )
        video_ids: list[str] = []
        while request and len(video_ids) < max_videos:
            response = request.execute()
            video_ids.extend(
                item["contentDetails"]["videoId"]
                for item in response.get("items", [])
                if item.get("contentDetails", {}).get("videoId")
            )
            next_page = response.get("nextPageToken")
            request = (
                youtube.playlistItems().list(
                    part="contentDetails",
                    playlistId=uploads_id,
                    maxResults=min(max_videos - len(video_ids), 50),
                    pageToken=next_page,
                )
                if next_page and len(video_ids) < max_videos
                else None
            )

        for start in range(0, min(len(video_ids), max_videos), 50):
            response = youtube.videos().list(
                part="snippet,contentDetails,statistics",
                id=",".join(video_ids[start:start + 50]),
            ).execute()
            rows.extend(_video_row(video) for video in response.get("items", []))
            save_rows(rows, output_path)
            print(f"Videos collected: {len(rows)}")
    except Exception as error:
        print(f"Video collection stopped: {_api_error(error)}")
    finally:
        save_rows(rows, output_path)

    print(f"Video collection completed with {len(rows)} videos: {output_path}")
    return output_path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--channel_handle", default=None)
    parser.add_argument("--channel_id", default=None)
    parser.add_argument("--max_videos", type=int, default=100)
    parser.add_argument("--output", default=None)
    args = parser.parse_args()
    collect_videos(**vars(args))


if __name__ == "__main__":
    main()
