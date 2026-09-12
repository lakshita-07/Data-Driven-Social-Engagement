"""Load processed CSV outputs into the configured MySQL database."""

from pathlib import Path

import pandas as pd

from src.database.connection import get_connection


ROOT = Path(__file__).resolve().parents[2]
SCHEMA_PATH = Path(__file__).with_name("schema.sql")


def mysql_value(value):
    if pd.isna(value):
        return None
    if isinstance(value, pd.Timestamp):
        return value.to_pydatetime().replace(tzinfo=None)
    return value


def initialize_schema(connection) -> None:
    statements = SCHEMA_PATH.read_text(encoding="utf-8").split(";")
    cursor = connection.cursor()
    for statement in statements:
        if statement.strip():
            cursor.execute(statement)
    cursor.close()


def migrate_existing_schema(connection) -> None:
    cursor = connection.cursor()
    migrations = {
        "posts": {
            "source_type": "VARCHAR(64) DEFAULT 'public_youtube_api'",
        },
        "comments": {
            "comment_like_count": "BIGINT NULL",
            "author_channel_id": "VARCHAR(128) NULL",
            "source_type": "VARCHAR(64) DEFAULT 'public_youtube_api'",
        },
    }
    for table, columns in migrations.items():
        cursor.execute(f"SHOW COLUMNS FROM {table}")
        existing = {row[0] for row in cursor.fetchall()}
        for column, definition in columns.items():
            if column not in existing:
                cursor.execute(
                    f"ALTER TABLE {table} ADD COLUMN {column} {definition}"
                )
    connection.commit()
    cursor.close()


def load_processed_outputs(processed: Path = ROOT / "data/processed") -> None:
    posts = pd.read_csv(processed / "posts_processed.csv")
    comments = pd.read_csv(processed / "comments_processed.csv")
    posts["posting_datetime"] = pd.to_datetime(
        posts["posting_datetime"], errors="coerce", utc=True
    )
    comments["comment_datetime"] = pd.to_datetime(
        comments["comment_datetime"], errors="coerce", utc=True
    )
    connection = get_connection()
    try:
        initialize_schema(connection)
        migrate_existing_schema(connection)
        cursor = connection.cursor()
        post_sql = """
            INSERT INTO posts (
                post_id, platform, account_id, content_type, caption, hashtags,
                posting_datetime, duration_seconds, views, likes, comments_count,
                shares, saves, retention_rate, source_type
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                platform=VALUES(platform), account_id=VALUES(account_id),
                content_type=VALUES(content_type), caption=VALUES(caption),
                hashtags=VALUES(hashtags), posting_datetime=VALUES(posting_datetime),
                duration_seconds=VALUES(duration_seconds), views=VALUES(views),
                likes=VALUES(likes), comments_count=VALUES(comments_count),
                shares=VALUES(shares), saves=VALUES(saves),
                retention_rate=VALUES(retention_rate), source_type=VALUES(source_type)
        """
        for row in posts.itertuples(index=False):
            cursor.execute(
                post_sql,
                (
                    *(
                        mysql_value(value)
                        for value in (
                            row.post_id, row.platform, row.account_id,
                            row.content_type, row.caption, row.hashtags,
                            row.posting_datetime, row.duration_seconds, row.views,
                            row.likes, row.comments_count, row.shares, row.saves,
                            row.retention_rate,
                        )
                    ),
                    "public_youtube_api",
                ),
            )

        comment_sql = """
            INSERT INTO comments (
                comment_id, post_id, comment_text, comment_datetime,
                source_type
            ) VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                post_id=VALUES(post_id), comment_text=VALUES(comment_text),
                comment_datetime=VALUES(comment_datetime),
                source_type=VALUES(source_type)
        """
        for row in comments.itertuples(index=False):
            cursor.execute(
                comment_sql,
                (
                    mysql_value(row.comment_id), mysql_value(row.post_id),
                    mysql_value(row.comment_text), mysql_value(row.comment_datetime),
                    "public_youtube_api",
                ),
            )
        connection.commit()
        cursor.close()
        print(f"Loaded {len(posts)} posts and {len(comments)} comments into MySQL.")
    finally:
        connection.close()


if __name__ == "__main__":
    load_processed_outputs()