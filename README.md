# Data-Driven Social Engagement Initiative

This project analyzes public YouTube content and audience comments to study
engagement, sentiment, relatability, topic resonance, and content strategy.
The current dataset is collected from the public **Psych2Go** channel using the
YouTube Data API v3.

## Current Dataset

- 100 Psych2Go videos
- 9,335 processed top-level comments
- 1,223 comments classified as `Relatable` by the rule-based baseline
- 90 long-form videos and 10 Shorts
- Raw source: `public_youtube_api`

These are cumulative public counts, not first-party analytics measurements.

## Project Structure

```text
.
|- run_pipeline.py                 # Demo/live orchestration entrypoint
|- dashboard/app.py                # Streamlit dashboard
|- content_series/                 # Proposed original content experiment
|- data/
|  |- raw/                         # Local YouTube API exports
|  |- processed/                   # Derived analysis tables and manifest
|  `- external/                    # Human labels, trend data, A/B inputs
|- docs/                           # Methodology, data dictionary, strategy report
|- src/
|  |- data_collection/             # YouTube collectors and deprecated fallback
|  |- feature_engineering/         # Content features and topic classification
|  |- models/                      # Virality, tests, trends, recommendations
|  |- nlp/                         # Sentiment and relatability analysis
|  |- preprocessing/               # Shared comment cleaning utilities
|  `- database/                    # Optional MySQL connection support
|- tests/                          # Automated tests
`- tools/                          # Annotation-batch utilities
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set the API key in `.env`. The public channel defaults are:

```text
YOUTUBE_CHANNEL_HANDLE=@Psych2go
DATA_SOURCE=public_youtube
```

Never commit `.env`, API keys, or unredacted raw exports.

## Technology Stack

- **Language:** Python 3.9+
- **Data processing:** Pandas and NumPy
- **Collection:** YouTube Data API v3, with a deprecated Selenium fallback
- **Text analysis:** TextBlob, regular-expression cleaning, and scikit-learn
- **Statistical modeling:** SciPy, scikit-learn, and Mann-Whitney/Kruskal-Wallis tests
- **Database:** MySQL via `mysql-connector-python`
- **Visualization:** Streamlit, with Pandas chart outputs
- **Storage:** CSV source/derived files plus MySQL `posts` and `comments` tables
- **Testing:** pytest

Instagram Graph API, Power BI, Tableau, and Jupyter notebooks are not used in
the current implementation. The project uses public Psych2Go YouTube data and
Streamlit instead.

## Live Psych2Go Pipeline

Collect public videos and comments, then regenerate all processed outputs:

```bash
python run_pipeline.py --mode live --collect \
  --max-videos 100 \
  --max-comments-per-video 100
```

To reuse existing raw files without making API requests:

```bash
python run_pipeline.py --mode live --skip-collect
```

To also load the processed Psych2Go data into MySQL, configure `DB_HOST`,
`DB_NAME`, `DB_USER`, and `DB_PASSWORD` in `.env`, create the database, and run:

```bash
python run_pipeline.py --mode live --skip-collect --use-database
```

The pipeline creates or updates the `posts` and `comments` tables using
`src/database/schema.sql`. CSV files remain the reproducible source export;
MySQL is the operational store.

Collection creates:

- `data/raw/youtube_videos_raw.csv`
- `data/raw/youtube_comments_raw.csv`

The collectors save partial results after collection begins and use exact
documented schemas. See `data/raw/README.md` for public-data limitations.

## Demo Pipeline

Demo mode uses clearly labeled synthetic inputs for testing the pipeline:

```bash
python run_pipeline.py
```

Demo results are separate from the live Psych2Go interpretation and must not be
reported as real channel evidence.

## Analysis Modules

The live pipeline runs these stages:

1. Raw CSV adaptation and cleaning
2. Content features and engagement rates
3. Engagement-reach virality proxy
4. Sentiment analysis with TextBlob
5. Rule-based `Relatable`/`Neutral` classification
6. Topic classification and resonance summaries
7. Format and timing comparisons
8. Recommendations
9. Optional trend forecasting and supervised model evaluation

Useful standalone commands:

```bash
python -m src.nlp.relatability_model
python -m src.models.trend_forecasting
python -m src.models.ab_testing
python -m src.models.ab_framework_validation
```

## Manual Relatability Labels

The reviewed file at `data/external/relatability_annotation_sample.csv` contains
60 labeled Psych2Go comments. To train the supervised baseline with that file:

```bash
python -m src.nlp.relatability_model \
  --labels data/external/relatability_annotation_sample.csv
```

Valid labels are exactly `Relatable` and `Neutral`. More manually reviewed rows
would improve evaluation reliability. Generated metrics are saved to
`data/processed/relatability_model_metrics.csv`.

## Dashboard

Start the Streamlit dashboard with:

```bash
streamlit run dashboard/app.py
```

It displays available video performance, topics, sentiment, relatability,
virality proxy rankings, recommendations, timing comparisons, trend forecasts,
and model/A-B outputs when those files exist.

## Optional Inputs

### Trend history

Create `data/external/keyword_history.csv` with real permitted observations:

```text
keyword,date,volume
burnout,2026-01-01,1200
burnout,2026-01-08,1400
burnout,2026-01-15,1800
```

### A/B results

Create `data/external/ab_test_results.csv` from a controlled experiment on
original content. Use two variants and at least two observations per variant:

```text
experiment_id,variant,metric_name,metric_value
hook_test,A,engagement_rate,3.2
hook_test,B,engagement_rate,4.1
```

The framework can be validated with simulated data, but simulated results are
not real content evidence.

## Outputs

Important files in `data/processed/` include:

- `posts_processed.csv`, `comments_processed.csv`
- `posts_features.csv`, `posts_topics.csv`, `posts_virality.csv`
- `comments_sentiment.csv`, `comments_relatability.csv`
- `topic_performance.csv`, `topic_relatability.csv`
- `format_analysis.csv`, `hourly_analysis.csv`, `day_analysis.csv`
- `recommendations.csv`, `historical_statistical_tests.csv`
- `relatability_model_metrics.csv`, `relatability_model_predictions.csv`
- `dataset_manifest.json`

## Limitations

Because Psych2Go is a third-party public channel, the YouTube Data API does
not provide owner-only analytics. Shares, saves or playlist additions,
retention/average view percentage, subscribers gained, follower growth, and
save-to-share ratios remain unavailable and are represented as blank/`NaN`.

The `virality_score` is therefore an engagement-and-reach proxy, not the
share/save-weighted viral coefficient described in the original proposal.
Historical counts are cumulative and observational; they do not establish
causal effects or replace a randomized experiment.

## Documentation and Validation

- [Data dictionary](docs/data_dictionary.md)
- [Methodology](docs/methodology.md)
- [Strategy report](docs/strategy_report.md)
- [Content series](content_series/README.md)

## Database

MySQL is supported as the project database. The default CSV workflow does not
require a running database, but `--use-database` loads the current processed
Psych2Go outputs into MySQL with idempotent upserts. Public-channel-only fields
such as shares, saves, retention, and subscribers gained are stored as `NULL`.

Run the full test suite with:

```bash
python -m pytest -q
```
