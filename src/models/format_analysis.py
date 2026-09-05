import pandas as pd


def main():

    input_path = "data/processed/posts_virality.csv"

    posts = pd.read_csv(input_path)

    print("Posts loaded:", len(posts))

    print()
    print("Performance by content type:")

    format_analysis = posts.groupby(
        "content_type"
    ).agg(
        video_count=("post_id", "count"),
        average_views=("views", "mean"),
        average_likes=("likes", "mean"),
        average_comments=("comments_count", "mean"),
        average_engagement_rate=("engagement_rate", "mean"),
        average_virality_score=("virality_score", "mean")
    ).reset_index()

    print(
        format_analysis.to_string(index=False)
    )

    print()
    print("Median performance by content type:")

    median_analysis = posts.groupby(
        "content_type"
    ).agg(
        median_views=("views", "median"),
        median_engagement_rate=("engagement_rate", "median"),
        median_virality_score=("virality_score", "median")
    ).reset_index()

    print(
        median_analysis.to_string(index=False)
    )

    output_path = "data/processed/format_analysis.csv"

    format_analysis.to_csv(
        output_path,
        index=False
    )

    print()
    print("Format analysis saved to:")
    print(output_path)


if __name__ == "__main__":
    main()