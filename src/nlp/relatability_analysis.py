import pandas as pd
import re


STRONG_RELATABILITY_PHRASES = [
    "relate",
    "relatable",
    "same here",
    "same bro",
    "same",
    "literally me",
    "this is me",
    "this is literally me",
    "me too",
    "i feel the same",
    "i feel this",
    "i can relate",
    "i relate",
    "so relatable",
    "this is exactly me",
    "this is exactly what i",
    "we all go through this",
    "not alone",
    "going through this"
]


STRUGGLE_WORDS = [
    "struggle",
    "struggling",
    "stress",
    "stressed",
    "anxiety",
    "anxious",
    "panic",
    "pressure",
    "burnout",
    "burned out",
    "tired",
    "exhausted",
    "lonely",
    "alone",
    "worried",
    "worry",
    "afraid",
    "fear",
    "confused",
    "overwhelmed"
]


PROBLEM_CONTEXT_WORDS = [
    "exam",
    "exams",
    "college",
    "student",
    "students",
    "parents",
    "marks",
    "job",
    "career",
    "money",
    "relationship",
    "relationships",
    "work",
    "school"
]


PERSONAL_PRONOUNS = [
    "i",
    "me",
    "my",
    "we",
    "our",
    "us"
]


def contains_phrase(text, phrase):
    pattern = r"\b" + re.escape(phrase) + r"\b"
    return re.search(pattern, text) is not None


def calculate_relatability_score(text):
    text = str(text).lower()

    score = 0

    for phrase in STRONG_RELATABILITY_PHRASES:
        if contains_phrase(text, phrase):
            score = score + 3

    for word in STRUGGLE_WORDS:
        if contains_phrase(text, word):
            score = score + 2

    has_personal_reference = False

    for word in PERSONAL_PRONOUNS:
        if contains_phrase(text, word):
            has_personal_reference = True
            break

    has_problem_context = False

    for word in PROBLEM_CONTEXT_WORDS:
        if contains_phrase(text, word):
            has_problem_context = True
            break

    if has_personal_reference and has_problem_context:
        score = score + 2

    if has_personal_reference and "feel" in text:
        score = score + 2

    return score


def classify_relatability(score):
    if score >= 3:
        return "Relatable"
    else:
        return "Neutral"


def main():
    input_path = "data/processed/comments_sentiment.csv"
    output_path = "data/processed/comments_relatability.csv"

    comments = pd.read_csv(input_path)

    print("Comments loaded:", len(comments))

    comments["relatability_score"] = comments["cleaned_text"].apply(
        calculate_relatability_score
    )

    comments["relatability"] = comments["relatability_score"].apply(
        classify_relatability
    )

    print()
    print("Relatability distribution:")
    print(comments["relatability"].value_counts())

    print()
    print("Average relatability score:")
    print(comments["relatability_score"].mean())

    print()
    print("Sample relatability results:")

    print(
        comments[
            [
                "cleaned_text",
                "sentiment",
                "relatability_score",
                "relatability"
            ]
        ].sample(30).to_string(index=False)
    )

    comments.to_csv(
        output_path,
        index=False
    )

    print()
    print("Relatability results saved to:")
    print(output_path)


if __name__ == "__main__":
    main()
    