import pandas as pd


def load_data():
    input_path = "data/processed/posts_features.csv"

    posts = pd.read_csv(input_path)

    return posts


def calculate_virality_score(posts):

    posts["virality_score"] = (
        posts["engagement_rate"]
        * posts["views"].rank(pct=True)
    )

    return posts


def classify_virality(score, low_threshold, high_threshold):

    if score >= high_threshold:
        return "High"

    elif score >= low_threshold:
        return "Medium"

    else:
        return "Low"


def main():

    posts = load_data()

    print("Posts loaded:", len(posts))

    posts = calculate_virality_score(posts)

    low_threshold = posts["virality_score"].quantile(0.33)
    high_threshold = posts["virality_score"].quantile(0.66)

    posts["virality_level"] = posts["virality_score"].apply(
        classify_virality,
        args=(low_threshold, high_threshold)
    )

    print()
    print("Virality distribution:")

    print(
        posts["virality_level"].value_counts()
    )

    print()
    print("Top 10 videos by virality score:")

    top_videos = posts.sort_values(
        "virality_score",
        ascending=False
    ).head(10)

    print(
        top_videos[
            [
                "post_id",
                "content_type",
                "views",
                "engagement_rate",
                "virality_score",
                "virality_level"
            ]
        ].to_string(index=False)
    )

    output_path = "data/processed/posts_virality.csv"

    posts.to_csv(
        output_path,
        index=False
    )

    print()
    print("Virality results saved to:")
    print(output_path)


if __name__ == "__main__":
    main()