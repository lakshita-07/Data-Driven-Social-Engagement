# Data-Driven Social Engagement Initiative

This project analyzes YouTube content performance and audience comments to study
engagement, virality proxies, relatability, and topic resonance.

## Current Dataset

- 107 YouTube videos
- 8,841 processed comments
- 643 comments classified as relatable by the rule-based first pass
- 60 Shorts and 47 long-form videos

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Database credentials and API keys belong in `.env`. Never commit secrets.

## Pipeline

The main processing order is:

```text
YouTube API -> MySQL -> preprocessing -> features -> topics -> virality proxy
		-> sentiment -> relatability -> topic resonance -> recommendations
```

Useful commands:

```bash
python -m src.models.topic_performance
python -m src.models.topic_relatability
python -m src.models.recommendation_engine
python -m src.nlp.relatability_model
python -m src.models.trend_forecasting
python -m unittest discover -s tests -v
streamlit run dashboard/app.py
```

The trend and supervised NLP commands require their documented external input
files. Without those files they stop with an explanatory message or create an
annotation template of 60 comments; they do not fabricate data.

## Dashboard

The Streamlit dashboard is in `dashboard/app.py`. It displays overview metrics,
format and topic comparisons, topic relatability, recommendations, sentiment,
virality-proxy rankings, and optional trend/model evaluation outputs.

## Outputs

Processed data is stored in `data/processed/`, including:

- `posts_features.csv`
- `posts_topics.csv`
- `posts_virality.csv`
- `topic_performance.csv`
- `topic_relatability.csv`
- `recommendations.csv`
- `comments_sentiment.csv`
- `comments_relatability.csv`

## Interpretation Rules

- Public YouTube Data API data does not provide arbitrary-video shares, saves, or
	retention. These fields remain unavailable; they are not invented.
- `virality_score` is a project-defined engagement-and-reach proxy, not the exact
	viral coefficient from the project specification.
- Current counts are observational and cumulative. They are not randomized A/B
	test results and should not be interpreted as causal effects.
- TextBlob sentiment, keyword topic classification, and rule-based relatability
	are baseline methods.

See `docs/strategy_report.md` for findings, recommendations, and the proposed
controlled experiment plan.
