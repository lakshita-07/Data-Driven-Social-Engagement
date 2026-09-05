import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

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
    WHERE platform = 'YouTube'
    """

    posts = pd.read_sql(query, engine)

    return posts


def preprocess_posts(posts):

    posts["posting_datetime"] = pd.to_datetime(
        posts["posting_datetime"]
    )

    numeric_columns = [
        "duration_seconds",
        "views",
        "likes",
        "comments_count"
    ]

    for column in numeric_columns:
        posts[column] = pd.to_numeric(
            posts[column],
            errors="coerce"
        )

    posts["likes"] = posts["likes"].fillna(0)
    posts["comments_count"] = posts["comments_count"].fillna(0)

    posts["caption"] = posts["caption"].fillna("")
    posts["hashtags"] = posts["hashtags"].fillna("")

    posts = posts.drop_duplicates(
        subset=["post_id"]
    )

    posts = posts.reset_index(drop=True)

    return posts


def main():

    print("Loading posts from MySQL...")

    posts = load_posts()

    print()
    print("Original posts:", len(posts))

    posts = preprocess_posts(posts)

    print()
    print("Posts after preprocessing:", len(posts))

    print()
    print("Missing values:")

    print(
        posts[
            [
                "views",
                "likes",
                "comments_count",
                "duration_seconds"
            ]
        ].isnull().sum()
    )

    print()
    print("Sample processed posts:")

    print(
        posts[
            [
                "post_id",
                "content_type",
                "duration_seconds",
                "views",
                "likes",
                "comments_count"
            ]
        ].head(10).to_string(index=False)
    )

    output_path = "data/processed/posts_processed.csv"

    posts.to_csv(
        output_path,
        index=False
    )

    print()
    print("Processed posts saved to:")
    print(output_path)


if __name__ == "__main__":
    main()