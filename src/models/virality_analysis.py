import pandas as pd


def load_data():
    input_path = "data/processed/posts_features.csv"

    posts = pd.read_csv(input_path)

    return posts


def calculate_virality_score(posts):
    posts = posts.copy()
    reach = posts["views"].replace(0, pd.NA)
    shares = posts.get("shares", pd.Series(0, index=posts.index)).fillna(0)
    saves = posts.get("saves", pd.Series(0, index=posts.index)).fillna(0)
    comments = posts["comments_count"].fillna(0)
    likes = posts["likes"].fillna(0)

    has_share_save_data = shares.gt(0).any() or saves.gt(0).any()
    if has_share_save_data:
        posts["virality_score"] = (
            (0.40 * shares + 0.30 * saves + 0.20 * comments + 0.10 * likes)
            / reach
            * 100
        ).fillna(0)
        posts["virality_score_type"] = "Weighted engagement score"
    else:
        # Public YouTube exports do not expose shares, saves, or retention.
        posts["virality_score"] = (
            posts["engagement_rate"].fillna(0)
            * posts["views"].rank(pct=True)
        )
        posts["virality_score_type"] = "YouTube engagement-reach proxy"

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