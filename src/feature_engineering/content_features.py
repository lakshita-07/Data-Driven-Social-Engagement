import pandas as pd


def load_posts():
    input_path = "data/processed/posts_processed.csv"

    posts = pd.read_csv(input_path)

    return posts


def calculate_features(posts):

    posts["like_rate"] = 0.0
    posts["comment_rate"] = 0.0
    posts["engagement_rate"] = 0.0
    posts["views_per_second"] = 0.0

    valid_views = posts["views"] > 0
    valid_duration = posts["duration_seconds"] > 0

    posts.loc[valid_views, "like_rate"] = (
        posts.loc[valid_views, "likes"]
        / posts.loc[valid_views, "views"]
    ) * 100

    posts.loc[valid_views, "comment_rate"] = (
        posts.loc[valid_views, "comments_count"]
        / posts.loc[valid_views, "views"]
    ) * 100

    posts.loc[valid_views, "engagement_rate"] = (
        (
            posts.loc[valid_views, "likes"]
            + posts.loc[valid_views, "comments_count"]
        )
        / posts.loc[valid_views, "views"]
    ) * 100

    posts.loc[valid_duration, "views_per_second"] = (
        posts.loc[valid_duration, "views"]
        / posts.loc[valid_duration, "duration_seconds"]
    )

    posts["posting_datetime"] = pd.to_datetime(
        posts["posting_datetime"]
    )

    posts["posting_hour"] = posts[
        "posting_datetime"
    ].dt.hour

    posts["posting_day"] = posts[
        "posting_datetime"
    ].dt.day_name()

    return posts


def main():

    posts = load_posts()

    print("Posts loaded:", len(posts))

    posts = calculate_features(posts)

    print()
    print("Feature engineering completed.")

    print()
    print(
        posts[
            [
                "post_id",
                "content_type",
                "views",
                "likes",
                "comments_count",
                "like_rate",
                "comment_rate",
                "engagement_rate",
                "views_per_second",
                "posting_hour",
                "posting_day"
            ]
        ].head(10).to_string(index=False)
    )

    output_path = "data/processed/posts_features.csv"

    posts.to_csv(
        output_path,
        index=False
    )

    print()
    print("Features saved to:")
    print(output_path)


if __name__ == "__main__":
    main()