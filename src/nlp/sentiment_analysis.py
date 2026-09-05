import pandas as pd
from textblob import TextBlob


def get_polarity(text):
    return TextBlob(text).sentiment.polarity


def get_sentiment(polarity):
    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    else:
        return "Neutral"


def main():
    input_path = "data/processed/comments_processed.csv"
    output_path = "data/processed/comments_sentiment.csv"

    comments = pd.read_csv(input_path)

    print("Comments loaded:", len(comments))

    comments["polarity"] = comments["cleaned_text"].apply(
        get_polarity
    )

    comments["sentiment"] = comments["polarity"].apply(
        get_sentiment
    )

    print()
    print("Sentiment distribution:")
    print(comments["sentiment"].value_counts())

    comments.to_csv(
        output_path,
        index=False
    )

    print()
    print("NLP results saved to:")
    print(output_path)


if __name__ == "__main__":
    main()
    