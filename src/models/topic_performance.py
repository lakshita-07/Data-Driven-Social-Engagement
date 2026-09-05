import pandas as pd


def main():

    input_path = "data/processed/posts_topics.csv"
    output_path = "data/processed/topic_performance.csv"

    posts = pd.read_csv(input_path)

    print("Posts loaded:", len(posts))

    topic_analysis = posts.groupby(
        "topic"
    ).agg(
        video_count=("post_id", "count"),
        average_views=("views", "mean"),
        median_views=("views", "median"),
        average_engagement_rate=("engagement_rate", "mean"),
        median_engagement_rate=("engagement_rate", "median"),
        average_virality_score=("virality_score", "mean"),
        median_virality_score=("virality_score", "median")
    ).reset_index()

    topic_analysis = topic_analysis.sort_values(
        "average_virality_score",
        ascending=False
    )

    print()
    print("Performance by topic:")

    print(
        topic_analysis.to_string(index=False)
    )

    topic_analysis.to_csv(
        output_path,
        index=False
    )

    print()
    print("Topic performance saved to:")
    print(output_path)


if __name__ == "__main__":
    main()
