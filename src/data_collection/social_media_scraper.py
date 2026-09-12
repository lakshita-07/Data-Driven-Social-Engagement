"""Deprecated Selenium fallback; the default pipeline uses the public API."""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from datetime import datetime, timezone
import re
import sys
import os

PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)

sys.path.insert(0, PROJECT_ROOT)

from src.database.connection import get_connection


def get_page_source(url):
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=options)

    driver.get(url)

    html = driver.page_source

    driver.quit()

    return html


def convert_duration(duration):
    if duration is None:
        return None

    duration = duration.replace("PT", "")

    hours = 0
    minutes = 0
    seconds = 0

    if "H" in duration:
        hours = int(duration.split("H")[0])
        duration = duration.split("H")[1]

    if "M" in duration:
        minutes = int(duration.split("M")[0])
        duration = duration.split("M")[1]

    if "S" in duration:
        seconds = int(duration.replace("S", ""))

    return (hours * 3600) + (minutes * 60) + seconds


def convert_datetime(date_value):
    if date_value is None:
        return None

    date_time = datetime.fromisoformat(date_value)

    if date_time.tzinfo is not None:
        date_time = date_time.astimezone(timezone.utc)
        date_time = date_time.replace(tzinfo=None)

    return date_time


def find_engagement_data(html):
    views = None
    likes = None
    comments = None

    view_match = re.search(r'"viewCount":"(\d+)"', html)

    if view_match:
        views = int(view_match.group(1))

    like_match = re.search(r'"likeCount":"(\d+)"', html)

    if like_match:
        likes = int(like_match.group(1))

    comment_match = re.search(r'"commentCount":"(\d+)"', html)

    if comment_match:
        comments = int(comment_match.group(1))

    return views, likes, comments


def extract_keywords(soup):
    keywords = soup.find("meta", {"name": "keywords"})

    if keywords:
        keyword_text = keywords.get("content")

        if keyword_text:
            keyword_list = keyword_text.split(",")

            cleaned_keywords = []

            for keyword in keyword_list:
                keyword = keyword.strip()

                if keyword:
                    cleaned_keywords.append(keyword)

            return ", ".join(cleaned_keywords)

    return None


def extract_video_data(html):
    soup = BeautifulSoup(html, "html.parser")

    title = soup.find("meta", {"property": "og:title"})
    description = soup.find("meta", {"property": "og:description"})
    url = soup.find("meta", {"property": "og:url"})
    image = soup.find("meta", {"property": "og:image"})
    upload_date = soup.find("meta", {"itemprop": "uploadDate"})
    duration = soup.find("meta", {"itemprop": "duration"})

    video_url = url.get("content") if url else None

    video_id = None

    if video_url and "v=" in video_url:
        video_id = video_url.split("v=")[1].split("&")[0]

    title_value = title.get("content") if title else None
    description_value = description.get("content") if description else None
    upload_date_value = upload_date.get("content") if upload_date else None
    duration_value = duration.get("content") if duration else None

    duration_seconds = convert_duration(duration_value)

    posting_datetime = convert_datetime(upload_date_value)

    hashtags = extract_keywords(soup)

    views, likes, comments = find_engagement_data(html)

    if title_value and description_value:
        caption = title_value + "\n\n" + description_value
    elif title_value:
        caption = title_value
    else:
        caption = description_value

    data = {
        "post_id": video_id,
        "platform": "YouTube",
        "account_id": None,
        "content_type": "Video",
        "caption": caption,
        "hashtags": hashtags,
        "posting_datetime": posting_datetime,
        "duration_seconds": duration_seconds,
        "views": views,
        "likes": likes,
        "comments_count": comments,
        "shares": None,
        "saves": None,
        "retention_rate": None,
        "url": video_url,
        "thumbnail": image.get("content") if image else None,
        "title": title_value,
        "description": description_value
    }

    return data


def save_to_mysql(data):
    connection = get_connection()

    cursor = connection.cursor()

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
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s,
        %s
    )
    ON DUPLICATE KEY UPDATE
        platform = VALUES(platform),
        account_id = VALUES(account_id),
        content_type = VALUES(content_type),
        caption = VALUES(caption),
        hashtags = VALUES(hashtags),
        posting_datetime = VALUES(posting_datetime),
        duration_seconds = VALUES(duration_seconds),
        views = VALUES(views),
        likes = VALUES(likes),
        comments_count = VALUES(comments_count),
        shares = VALUES(shares),
        saves = VALUES(saves),
        retention_rate = VALUES(retention_rate)
    """

    values = (
        data["post_id"],
        data["platform"],
        data["account_id"],
        data["content_type"],
        data["caption"],
        data["hashtags"],
        data["posting_datetime"],
        data["duration_seconds"],
        data["views"],
        data["likes"],
        data["comments_count"],
        data["shares"],
        data["saves"],
        data["retention_rate"]
    )

    cursor.execute(query, values)

    connection.commit()

    cursor.close()
    connection.close()

    print("\nData successfully saved to MySQL")


def main():
    url = "https://www.youtube.com/watch?v=fHFOANOHwh8"

    print("Collecting page data...")

    html = get_page_source(url)

    video_data = extract_video_data(html)

    print("\nEXTRACTED VIDEO DATA:\n")

    for key, value in video_data.items():
        print(key, ":", value)

    save_to_mysql(video_data)


if __name__ == "__main__":
    main()