import pandas as pd
from scipy.stats import kruskal, mannwhitneyu


def compare_groups(posts, column, metric="engagement_rate", alpha=0.05):
    """Compare all groups in a categorical column with Kruskal-Wallis."""
    groups = []
    for group_name, group in posts.groupby(column):
        values = pd.to_numeric(group[metric], errors="coerce").dropna()
        if len(values) >= 2:
            groups.append((group_name, values))
    if len(groups) < 2:
        return {
            "comparison": column,
            "test": "Kruskal-Wallis",
            "group_count": len(groups),
            "statistic": float("nan"),
            "p_value": float("nan"),
            "statistically_significant": False,
        }
    statistic, p_value = kruskal(*(values for _, values in groups))
    return {
        "comparison": column,
        "test": "Kruskal-Wallis",
        "group_count": len(groups),
        "statistic": statistic,
        "p_value": p_value,
        "statistically_significant": p_value < alpha,
    }


def main():

    input_path = "data/processed/posts_virality.csv"

    posts = pd.read_csv(input_path)

    short_engagement = posts[posts["content_type"] == "Short"]["engagement_rate"]

    long_engagement = posts[
        posts["content_type"] == "Long-form"
    ]["engagement_rate"]

    statistic, p_value = mannwhitneyu(
        short_engagement,
        long_engagement,
        alternative="two-sided"
    )

    print("Statistical comparison: Short vs Long-form")
    print()

    print("Short videos:", len(short_engagement))
    print("Long-form videos:", len(long_engagement))

    print()
    print("Short median engagement rate:",
          short_engagement.median())

    print("Long-form median engagement rate:",
          long_engagement.median())

    print()
    print("Mann-Whitney U statistic:", statistic)
    print("P-value:", p_value)

    print()

    if p_value < 0.05:
        print("Result: Statistically significant difference.")
    else:
        print("Result: No statistically significant difference.")

    comparisons = pd.DataFrame(
        [
            compare_groups(posts, "content_type"),
            compare_groups(posts, "posting_hour"),
            compare_groups(posts, "posting_day"),
            compare_groups(posts, "video_length_group"),
        ]
    )
    comparisons.to_csv("data/processed/historical_statistical_tests.csv", index=False)


if __name__ == "__main__":
    main()
    