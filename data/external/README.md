# External Trend Data

Place a real external keyword or hashtag history file at:

```text
data/external/keyword_history.csv
```

The CSV must contain:

```text
keyword,date,volume
burnout,2026-01-01,1200
burnout,2026-01-08,1400
burnout,2026-01-15,1800
```

`volume` should be the metric supplied by the external source, such as search
interest or hashtag volume. Do not fill this file with invented values. Run the
forecast only after collecting real dated observations from a permitted source.

## Relatability Labels

Run the annotation workflow to create a review file:

```bash
python -m src.nlp.relatability_model
```

Review the generated 60-row `relatability_annotation_sample.csv` and fill its
`label` column with only `Relatable` or `Neutral`. Save the reviewed file as
`relatability_labels.csv`, then rerun the command to produce holdout evaluation
metrics. The existing rule-based labels are not used as ground truth.

## Controlled A/B Results

For a controlled content experiment, create
`data/external/ab_test_results.csv` with one row per observation:

```text
experiment_id,variant,metric_name,metric_value
hook_test,A,engagement_rate,3.2
hook_test,B,engagement_rate,4.1
```

Use exactly two variants per experiment and at least two observations per
variant. Run:

```bash
python -m src.models.ab_testing
```

The result is a Mann-Whitney U comparison. It reports evidence within the
experiment; it does not turn an observational historical comparison into an
A/B test. To validate the statistical framework against known effects without
claiming real-world evidence, run:

```bash
python -m src.models.ab_framework_validation
```

## Annotation protocol

Use `tools/build_label_batch.py` to create a stratified, decision-boundary-
focused review batch at `relatability_labels.csv`. Review each row manually
and set `label` to exactly `Relatable` or `Neutral`; do not copy the suggested
rule-based label blindly. The optional `confidence` field is `1` for unsure
and `2` for sure.

**Relatable** means the commenter expresses personal identification with the
struggle: first-person identification, disclosure of their own experience, or
language such as "this is me" or "I thought I was the only one".

**Neutral** includes generic praise, questions, off-topic comments, criticism,
bots, and agreement without personal identification. "So true" alone is
Neutral. Emoji-only comments are excluded. Judge sarcasm by its surface meaning
and mark uncertain cases with confidence `1`.

At least 20 valid rows and both classes are required by the model. A target of
300 rows is recommended for a stable comparison between the rule baseline and
TF-IDF plus logistic regression. Generated labels are not valid evidence.

Raw source exports may contain private or redistributable material and remain
local by default. Do not commit API keys or unredacted personal data.