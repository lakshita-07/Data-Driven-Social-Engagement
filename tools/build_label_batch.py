"""Build a stratified and decision-boundary-focused annotation batch."""

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "comments_relatability.csv"
OUTPUT = ROOT / "data" / "external" / "relatability_labels.csv"


def build_batch(sample_size: int = 300) -> pd.DataFrame:
    comments = pd.read_csv(INPUT)
    text_column = "cleaned_text"
    comments = comments[
        comments[text_column].fillna("").str.split().str.len().between(3, 60)
    ].copy()
    comments = comments.drop_duplicates("comment_id")
    if comments.empty:
        raise ValueError("No usable comments are available for annotation")

    comments["score_band"] = pd.qcut(
        comments["relatability_score"], q=4, labels=False, duplicates="drop"
    )
    per_band = max(1, int(sample_size * 0.60 / comments["score_band"].nunique()))
    stratified = (
        comments.groupby("score_band", group_keys=False)
        .apply(lambda group: group.sample(min(per_band, len(group)), random_state=42))
        .reset_index(drop=True)
    )
    boundary = comments.loc[
        (comments["relatability_score"] - 2.0).abs().sort_values().index
    ].head(int(sample_size * 0.40))
    batch = pd.concat([stratified, boundary], ignore_index=True)
    batch = batch.drop_duplicates("comment_id").sample(frac=1, random_state=42)
    batch = batch.head(min(sample_size, len(batch)))
    return batch[["comment_id", "post_id", "comment_text", text_column, "relatability_score"]].assign(
        label="", confidence=""
    )


def main() -> None:
    batch = build_batch()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    batch.to_csv(OUTPUT, index=False)
    print(f"Created {len(batch)} rows at {OUTPUT}")
    print("Fill label with Relatable or Neutral before training.")


if __name__ == "__main__":
    main()
