import pandas as pd
from scipy.stats import kruskal


def main():

    input_path = "data/processed/posts_virality.csv"

    posts = pd.read_csv(input_path)

    print("Posts loaded:", len(posts))

    print()
    print("Testing posting hour...")

    hourly_groups = []

    for hour in sorted(posts["posting_hour"].dropna().unique()):
        group = posts[
            posts["posting_hour"] == hour
        ]["engagement_rate"]

        if len(group) >= 2:
            hourly_groups.append(group)

    statistic, p_value = kruskal(*hourly_groups)

    print("Kruskal-Wallis statistic:", statistic)
    print("P-value:", p_value)

    if p_value < 0.05:
        print("Result: Posting hour has a statistically significant effect.")
    else:
        print("Result: No statistically significant difference by posting hour.")

    print()
    print("Testing posting day...")

    day_groups = []

    for day in posts["posting_day"].dropna().unique():
        group = posts[
            posts["posting_day"] == day
        ]["engagement_rate"]

        if len(group) >= 2:
            day_groups.append(group)

    statistic, p_value = kruskal(*day_groups)

    print("Kruskal-Wallis statistic:", statistic)
    print("P-value:", p_value)

    if p_value < 0.05:
        print("Result: Posting day has a statistically significant effect.")
    else:
        print("Result: No statistically significant difference by posting day.")


if __name__ == "__main__":
    main()