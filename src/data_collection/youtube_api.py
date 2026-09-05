from googleapiclient.discovery import build
from dotenv import load_dotenv
from datetime import datetime, timezone
from src.database.connection import get_connection
import os

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

SEARCH_QUERIES = [
   "student college struggles",
    "student procrastination productivity",
    "career job anxiety",
    "relationship social life struggles",
    "money financial struggles",
    "burnout academic pressure"
]

MAX_RESULTS_PER_QUERY = 10


def get_youtube_service():
    youtube = build(
        "youtube",
        "v3",
        developerKey=API_KEY
    )

    return youtube


def search_videos(youtube, query):
    request = youtube.search().list(
        part="id",
        q=query,
        type="video",
        maxResults=MAX_RESULTS_PER_QUERY
    )

    response = request.execute()

    video_ids = []

    for item in response["items"]:
        video_ids.append(item["id"]["videoId"])

    return video_ids


def get_video_details(youtube, video_ids):
    all_videos = []

    start = 0

    while start < len(video_ids):
        batch = video_ids[start:start + 50]

        video_ids_string = ",".join(batch)

        request = youtube.videos().list(
            part="snippet,contentDetails,statistics",
            id=video_ids_string
        )

        response = request.execute()

        for video in response["items"]:
            all_videos.append(video)

        start = start + 50

    return all_videos

def duration_to_seconds(duration):
    duration = duration.replace("PT", "")

    hours = 0
    minutes = 0
    seconds = 0

    if "H" in duration:
        parts = duration.split("H")
        hours = int(parts[0])
        duration = parts[1]

    if "M" in duration:
        parts = duration.split("M")
        minutes = int(parts[0])
        duration = parts[1]

    if "S" in duration:
        parts = duration.split("S")
        seconds = int(parts[0])

    return (hours * 3600) + (minutes * 60) + seconds


def convert_datetime(date_string):
    date_time = datetime.fromisoformat(
        date_string.replace("Z", "+00:00")
    )

    date_time = date_time.astimezone(timezone.utc)

    return date_time.replace(tzinfo=None)


def get_content_type(duration_seconds):
    if duration_seconds <= 60:
        return "Short"

    return "Long-form"


def save_video_to_database(video):
    connection = get_connection()
    cursor = connection.cursor()

    video_id = video["id"]
    snippet = video["snippet"]
    content_details = video["contentDetails"]
    statistics = video["statistics"]

    title = snippet.get("title")
    description = snippet.get("description")
    channel_id = snippet.get("channelId")
    published_at = snippet.get("publishedAt")

    duration = content_details.get("duration")

    views = statistics.get("viewCount")
    likes = statistics.get("likeCount")
    comments = statistics.get("commentCount")

    if views is not None:
        views = int(views)

    if likes is not None:
        likes = int(likes)

    if comments is not None:
        comments = int(comments)

    duration_seconds = duration_to_seconds(duration)

    content_type = get_content_type(duration_seconds)

    posting_datetime = convert_datetime(published_at)

    hashtags = ""

    if "tags" in snippet:
        hashtags = ", ".join(snippet["tags"])

    query = """
    INSERT INTO posts (
        post_id,
        platform,
        account_id,
        content_type,
        caption,
        hashtags,
        posting_datetime,
        duration_seconds,
        views,
        likes,
        comments_count,
        shares,
        saves,
        retention_rate
    )
    VALUES (
        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
    )
    ON DUPLICATE KEY UPDATE
        account_id = VALUES(account_id),
        content_type = VALUES(content_type),
        caption = VALUES(caption),
        hashtags = VALUES(hashtags),
        posting_datetime = VALUES(posting_datetime),
        duration_seconds = VALUES(duration_seconds),
        views = VALUES(views),
        likes = VALUES(likes),
        comments_count = VALUES(comments_count)
    """

    values = (
        video_id,
        "YouTube",
        channel_id,
        content_type,
        title + "\n\n" + description,
        hashtags,
        posting_datetime,
        duration_seconds,
        views,
        likes,
        comments,
        None,
        None,
        None
    )

    cursor.execute(query, values)

    connection.commit()

    cursor.close()
    connection.close()


def update_existing_content_types():
    connection = get_connection()
    cursor = connection.cursor()

    query = """
    UPDATE posts
    SET content_type =
        CASE
            WHEN duration_seconds <= 60 THEN 'Short'
            ELSE 'Long-form'
        END
    WHERE platform = 'YouTube'
    """

    cursor.execute(query)

    connection.commit()

    print("Existing YouTube records classified:", cursor.rowcount)

    cursor.close()
    connection.close()


def main():
    print("Starting YouTube data collection...")
    print()

    update_existing_content_types()

    print()

    youtube = get_youtube_service()

    all_video_ids = []

    for query in SEARCH_QUERIES:
        print("Searching:", query)

        video_ids = search_videos(youtube, query)

        for video_id in video_ids:
            if video_id not in all_video_ids:
                all_video_ids.append(video_id)

    print()
    print("Unique videos found:", len(all_video_ids))
    print()

    videos = get_video_details(youtube, all_video_ids)

    print("Saving videos to MySQL...")
    print()

    saved_count = 0

    for video in videos:
        save_video_to_database(video)

        print(
            "Saved:",
            video["snippet"]["title"]
        )

        saved_count = saved_count + 1

    print()
    print("Collection completed.")
    print("Videos processed:", saved_count)


if __name__ == "__main__":
    main()