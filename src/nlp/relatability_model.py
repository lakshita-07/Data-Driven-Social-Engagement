import argparse
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BASE_DIR = Path(__file__).resolve().parents[2]
COMMENTS_PATH = BASE_DIR / "data" / "processed" / "comments_relatability.csv"
LABELS_PATH = BASE_DIR / "data" / "external" / "relatability_labels.csv"
SAMPLE_PATH = BASE_DIR / "data" / "external" / "relatability_annotation_sample.csv"
METRICS_PATH = BASE_DIR / "data" / "processed" / "relatability_model_metrics.csv"
PREDICTIONS_PATH = BASE_DIR / "data" / "processed" / "relatability_model_predictions.csv"
VALID_LABELS = {"Relatable", "Neutral"}


def create_annotation_sample(
    comments_path: Path = COMMENTS_PATH,
    output_path: Path = SAMPLE_PATH,
    sample_size: int = 60,
) -> pd.DataFrame:
    comments = pd.read_csv(comments_path)
    sample_size = min(sample_size, len(comments))
    sample = comments.sample(n=sample_size, random_state=42)[
        ["comment_id", "comment_text", "cleaned_text", "relatability"]
    ].copy()
    sample = sample.rename(columns={"relatability": "suggested_label"})
    sample["label"] = ""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(output_path, index=False)
    return sample


def train_and_evaluate(
    labels_path: Path = LABELS_PATH,
    comments_path: Path = COMMENTS_PATH,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    labels = pd.read_csv(labels_path)
    required = {"comment_id", "label"}
    missing = required.difference(labels.columns)
    if missing:
        raise ValueError(
            f"Labels are missing required columns: {', '.join(sorted(missing))}"
        )

    labels["label"] = labels["label"].astype(str).str.strip()
    invalid_labels = set(labels["label"]) - VALID_LABELS
    if invalid_labels:
        raise ValueError(f"Unsupported labels: {sorted(invalid_labels)}")

    comments = pd.read_csv(comments_path, usecols=["comment_id", "cleaned_text"])
    data = labels.merge(comments, on="comment_id", how="inner", validate="one_to_one")
    data = data.dropna(subset=["cleaned_text"])
    if data["label"].nunique() < 2:
        raise ValueError("Manual labels must contain both Relatable and Neutral classes")
    if len(data) < 20:
        raise ValueError("At least 20 manually labeled comments are required")

    train_text, test_text, train_labels, test_labels = train_test_split(
        data["cleaned_text"],
        data["label"],
        test_size=0.2,
        random_state=42,
        stratify=data["label"],
    )
    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)),
            ("classifier", LogisticRegression(max_iter=1000, class_weight="balanced")),
        ]
    )
    model.fit(train_text, train_labels)
    predictions = model.predict(test_text)

    report = classification_report(
        test_labels,
        predictions,
        labels=["Relatable", "Neutral"],
        output_dict=True,
        zero_division=0,
    )
    metrics = pd.DataFrame(
        [
            {
                "metric": label,
                "precision": values.get("precision"),
                "recall": values.get("recall"),
                "f1_score": values.get("f1-score"),
                "support": values.get("support"),
            }
            for label, values in report.items()
            if isinstance(values, dict)
        ]
    )
    test_results = data.loc[test_text.index, ["comment_id", "label"]].copy()
    test_results["predicted_label"] = predictions
    return metrics, test_results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", type=Path, default=LABELS_PATH)
    parser.add_argument("--sample-output", type=Path, default=SAMPLE_PATH)
    parser.add_argument("--sample-size", type=int, default=60)
    args = parser.parse_args()

    if not args.labels.exists():
        create_annotation_sample(output_path=args.sample_output, sample_size=args.sample_size)
        print(f"Annotation sample created at: {args.sample_output}")
        print("Review each row and fill label with Relatable or Neutral.")
        print(f"Then rerun with --labels {args.labels}")
        return

    metrics, predictions = train_and_evaluate(labels_path=args.labels)
    metrics.to_csv(METRICS_PATH, index=False)
    predictions.to_csv(PREDICTIONS_PATH, index=False)
    print(metrics.to_string(index=False))
    print(f"\nMetrics saved to: {METRICS_PATH}")
    print(f"Predictions saved to: {PREDICTIONS_PATH}")


if __name__ == "__main__":
    main()