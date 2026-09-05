import pandas as pd
from scipy.stats import mannwhitneyu


def main():

    input_path = "data/processed/posts_virality.csv"

    posts = pd.read_csv(input_path)

    short_engagement = posts[
        posts["content_type"] == "Short"
    ]["engagement_rate"]

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


if __name__ == "__main__":
    main()
    