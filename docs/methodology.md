# Methodology

## Pipeline

`run_pipeline.py` regenerates derived outputs in this order:

1. Feature engineering
2. Virality analysis
3. Sentiment analysis
4. Rule-based relatability
5. Topic classification
6. Topic, format, and timing summaries
7. Historical statistical comparisons
8. Recommendations
9. Optional supervised and controlled-experiment steps

## Metrics

Engagement rate is:

$$
100 \times \frac{likes + comments}{views}
$$

When share and save counts are available, the weighted virality score is:

$$
100 \times \frac{0.40 shares + 0.30 saves + 0.20 comments + 0.10 likes}{views}
$$

Public YouTube exports usually do not expose shares, saves, or retention. In
that case the project records a `YouTube engagement-reach proxy` based on
engagement rate and percentile-ranked views. It is not a causal or predictive
viral coefficient.

The implemented public-data proxy is:

$$
	ext{Virality Proxy} = \text{Engagement Rate} \times \text{Percentile Rank(Views)}
$$

Additional derived features are:

$$
	ext{Like Rate} = 100 \times \frac{likes}{views}
$$

$$
	ext{Comment Rate} = 100 \times \frac{comments}{views}
$$

$$
	ext{Views per Second} = \frac{views}{duration\_seconds}
$$

The rule-based relatability score adds 3 points for strong identification
phrases, 2 points for struggle words, 2 points when personal references occur
with problem context, and 2 points when a personal reference occurs with
`feel`. A score of at least 3 is classified as `Relatable`; otherwise it is
`Neutral`.

Topic recommendation scores use percentile-ranked metrics:

$$
	ext{Topic Recommendation} =
0.40E + 0.35V + 0.25R
$$

where $E$ is engagement percentile, $V$ is virality-proxy percentile, and $R$
is relatable-comment-rate percentile. Format and timing recommendations use
0.55 engagement percentile and 0.45 virality-proxy percentile.

## Text analysis

TextBlob provides a baseline polarity score. Relatability is initially scored
with phrase, struggle-context, and personal-reference rules. The optional
TF-IDF plus logistic-regression model requires a separate human-reviewed file
at `data/external/relatability_labels.csv` with `comment_id` and a label of
`Relatable` or `Neutral`.

## Statistical interpretation

Historical group comparisons use Kruskal-Wallis tests for multiple groups.
These are observational comparisons, not randomized A/B tests. A controlled
experiment may be analyzed with `src/models/ab_testing.py` after observations
are supplied in `data/external/ab_test_results.csv`.

The controlled A/B module uses a two-sided Mann-Whitney U test, reports the
mean difference between variants, relative effect percentage, p-value, and
whether the result is statistically significant at the chosen alpha level.

## Limitations

- Metrics are cumulative and may reflect different exposure periods.
- Topic labels are keyword-based and can be imperfect.
- Small groups should be treated cautiously.
- Correlation or group differences do not establish causation.
- Comments may contain sensitive personal information; keep raw exports local.
