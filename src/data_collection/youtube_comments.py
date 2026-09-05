from googleapiclient.discovery import build
from dotenv import load_dotenv
from src.database.connection import get_connection
from datetime import datetime
import os

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")


def get_youtube_service():
    youtube = build(
        "youtube",
        "v3",
        developerKey=API_KEY
    )
    return youtube


def get_video_ids():
    connection = get_connection()
    cursor = connection.cursor()

    query = """
    SELECT post_id
    FROM posts
    WHERE platform = 'YouTube'
    """

    cursor.execute(query)

    video_ids = []

    for row in cursor.fetchall():
        video_ids.append(row[0])

    cursor.close()
    connection.close()

    return video_ids


def convert_datetime(date_string):
    date_time = datetime.fromisoformat(
        date_string.replace("Z", "+00:00")
    )

    date_time = date_time.replace(tzinfo=None)

    return date_time


def get_comments(youtube, video_id):
    comments = []

    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100,
            textFormat="plainText"
        )

        response = request.execute()

        for item in response["items"]:
            comment = item["snippet"]["topLevelComment"]["snippet"]

            comment_id = item["snippet"]["topLevelComment"]["id"]
            comment_text = comment["textDisplay"]
            comment_datetime = convert_datetime(
                comment["publishedAt"]
            )

            comments.append({
                "comment_id": comment_id,
                "post_id": video_id,
                "comment_text": comment_text,
                "comment_datetime": comment_datetime
            })

    except Exception as error:
        print("Could not collect comments for:", video_id)
        print(error)

    return comments


def save_comments(comments):
    if len(comments) == 0:
        return

    connection = get_connection()
    cursor = connection.cursor()

    query = """
    INSERT INTO comments (
        comment_id,
        post_id,
        comment_text,
        comment_datetime
    )
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
        comment_text = VALUES(comment_text),
        comment_datetime = VALUES(comment_datetime)
    """

    for comment in comments:
        values = (
            comment["comment_id"],
            comment["post_id"],
            comment["comment_text"],
            comment["comment_datetime"]
        )

        cursor.execute(query, values)

    connection.commit()

    cursor.close()
    connection.close()


def main():
    print("Starting YouTube comment collection...")
    print()

    youtube = get_youtube_service()

    video_ids = get_video_ids()

    print("Videos found:", len(video_ids))
    print()

    total_comments = 0

    for video_id in video_ids:
        print("Collecting comments for:", video_id)

        comments = get_comments(youtube, video_id)

        save_comments(comments)

        total_comments = total_comments + len(comments)

        print("Comments collected:", len(comments))
        print()

    print("Comment collection completed.")
    print("Total comments collected:", total_comments)


if __name__ == "__main__":
    main()