import pandas as pd


TOPIC_KEYWORDS = {
    "Academic Pressure": [
        "student",
        "college",
        "exam",
        "academic",
        "study",
        "school",
        "marks"
    ],
    "Procrastination and Productivity": [
        "procrastination",
        "productivity",
        "motivation",
        "discipline",
        "productive",
        "time management"
    ],
    "Career and Job Anxiety": [
        "career",
        "job",
        "work",
        "interview",
        "employment",
        "future"
    ],
    "Relationships and Social Life": [
        "relationship",
        "relationships",
        "friends",
        "friendship",
        "social",
        "dating",
        "lonely",
        "love"
    ],
    "Money and Financial Struggles": [
        "money",
        "financial",
        "finance",
        "salary",
        "income",
        "debt",
        "saving"
    ],
    "Burnout and Mental Pressure": [
        "burnout",
        "burned out",
        "stress",
        "stressed",
        "anxiety",
        "anxious",
        "pressure",
        "tired",
        "exhausted",
        "overwhelmed"
    ]
}


def classify_topic(text):

    text = str(text).lower()

    topic_scores = {}

    for topic, keywords in TOPIC_KEYWORDS.items():

        score = 0

        for keyword in keywords:

            if keyword in text:
                score = score + 1

        topic_scores[topic] = score

    best_topic = max(
        topic_scores,
        key=topic_scores.get
    )

    if topic_scores[best_topic] == 0:
        return "Other"

    return best_topic


def main():

    input_path = "data/processed/posts_virality.csv"
    output_path = "data/processed/posts_topics.csv"

    posts = pd.read_csv(input_path)

    print("Posts loaded:", len(posts))

    posts["topic"] = (
        posts["caption"]
        .fillna("")
        .apply(classify_topic)
    )

    print()
    print("Topic distribution:")

    print(
        posts["topic"].value_counts()
    )

    print()
    print("Sample topic classifications:")

    print(
        posts[
            [
                "post_id",
                "topic",
                "caption"
            ]
        ].head(20).to_string(index=False)
    )

    posts.to_csv(
        output_path,
        index=False
    )

    print()
    print("Topic results saved to:")
    print(output_path)


if __name__ == "__main__":
    main()