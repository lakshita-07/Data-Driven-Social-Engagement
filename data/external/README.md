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
A/B test.