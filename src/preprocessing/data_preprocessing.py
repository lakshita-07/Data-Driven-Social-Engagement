import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import re

load_dotenv()

DB_HOST = os.getenv("DB_host")
DB_USER = os.getenv("DB_user")
DB_PASSWORD = os.getenv("DB_password")
DB_NAME = os.getenv("DB_name")

engine = create_engine(
    f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
)


def load_posts():
    query = """
    SELECT *
    FROM posts
    """

    posts = pd.read_sql(query, engine)

    return posts


def load_comments():
    query = """
    SELECT *
    FROM comments
    """

    comments = pd.read_sql(query, engine)

    return comments


def clean_comment(text):
    text = text.lower()

    text = re.sub(r"http\S+|www\S+", "", text)

    text = re.sub(r"#(\w+)", r"\1", text)

    text = re.sub(
        r"[^\w\s!?.,'😊😂🤣😍❤️🔥😢😭😡👍👏🙏]",
        "",
        text
    )

    text = re.sub(r"\s+", " ", text)

    text = text.strip()

    return text


def preprocess_comments(comments):
    comments["cleaned_text"] = comments["comment_text"].apply(
        clean_comment
    )

    comments = comments[
        comments["cleaned_text"].str.len() > 0
    ]

    comments = comments.reset_index(drop=True)

    return comments


def save_processed_comments(comments):
    output_path = "data/processed/comments_processed.csv"

    comments.to_csv(
        output_path,
        index=False
    )

    print()
    print("Processed comments saved to:")
    print(output_path)


def main():
    print("Loading project data...")

    posts = load_posts()
    comments = load_comments()

    print()
    print("Original posts:", len(posts))
    print("Original comments:", len(comments))

    comments = preprocess_comments(comments)

    print()
    print("Comments after preprocessing:", len(comments))

    save_processed_comments(comments)


if __name__ == "__main__":
    main()