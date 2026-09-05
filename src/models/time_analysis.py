import pandas as pd


def main():

    input_path = "data/processed/posts_virality.csv"

    posts = pd.read_csv(input_path)

    print("Posts loaded:", len(posts))

    print()
    print("Performance by posting hour:")

    hourly_analysis = posts.groupby(
        "posting_hour"
    ).agg(
        video_count=("post_id", "count"),
        average_views=("views", "mean"),
        median_views=("views", "median"),
        average_engagement_rate=("engagement_rate", "mean"),
        median_engagement_rate=("engagement_rate", "median")
    ).reset_index()

    print(
        hourly_analysis.to_string(index=False)
    )

    print()
    print("Performance by posting day:")

    day_analysis = posts.groupby(
        "posting_day"
    ).agg(
        video_count=("post_id", "count"),
        average_views=("views", "mean"),
        median_views=("views", "median"),
        average_engagement_rate=("engagement_rate", "mean"),
        median_engagement_rate=("engagement_rate", "median")
    ).reset_index()

    print(
        day_analysis.to_string(index=False)
    )

    hourly_analysis.to_csv(
        "data/processed/hourly_analysis.csv",
        index=False
    )

    day_analysis.to_csv(
        "data/processed/day_analysis.csv",
        index=False
    )

    print()
    print("Time analysis saved.")


if __name__ == "__main__":
    main()