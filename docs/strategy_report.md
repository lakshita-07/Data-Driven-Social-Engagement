# Strategy Report

## Objective

Identify content topics and formats associated with stronger YouTube engagement
and audience resonance, while keeping unavailable metrics and observational
limitations explicit.

## Evidence Base

The current dataset contains 100 Psych2Go videos and 9,335 processed comments.
The analysis uses current cumulative views, likes, and comments, plus derived
engagement and virality-proxy metrics. Comments are linked to videos through
`post_id`.

## Findings

### Format

Shorts have higher observed reach than long-form videos in this sample, but the
Mann-Whitney test found no statistically significant difference in engagement
rate (`p = 0.1188`). This is a descriptive difference, not evidence that Shorts
cause higher engagement.

### Timing

The Kruskal-Wallis tests found no statistically significant engagement-rate
difference by posting hour (`p = 0.6768`) or posting day (`p = 0.6113`). Posting
time should therefore be treated as an experiment variable, not a proven
optimization.

### Topics and Resonance

The topic-relatability analysis joins comments to the keyword-classified topic
of their video. Burnout and Mental Pressure has the highest observed relatable
comment rate, while Academic Pressure has the largest comment volume. Topic
sample sizes and the rule-based classifier mean these results need validation
with manually labeled comments.

### Virality

The project uses an engagement-based virality proxy because public YouTube data
does not expose arbitrary-video shares, saves, or retention. The proxy is useful
for ranking this dataset, but must not be reported as the official viral
coefficient.

## Current Recommendations

1. Use topic and format rankings as hypotheses for future content, not guarantees.
2. Prioritize controlled tests around relatable struggle framing, especially
   burnout and academic-pressure themes.
3. Collect first-party shares, saves, retention, and follower-growth metrics for
   the project’s own content series.
4. Keep posting time as an experimental factor because current evidence does not
   establish a best time.
5. Manually label the generated relatability annotation sample before reporting
   supervised model metrics.

## Controlled Experiment Plan

For a true A/B test, publish matched content pairs where one variable changes at
a time: Short versus long-form, visual versus text hook, caption style, or
posting window. Randomize assignment where possible, record first-party metrics
at fixed intervals, and predefine the primary outcome such as engagement rate
or retention. Analyze confidence intervals and multiple comparisons before
making a strategy claim.

## Remaining Risks

- Historical cumulative counts do not equal performance measured at publication.
- Keyword topic classification can miss context and ambiguous language.
- TextBlob sentiment can misread sarcasm, jokes, and emojis.
- Rule-based relatability is a first-pass classifier, not ground truth.
- External trend forecasting cannot run until real dated keyword history is
  collected from a permitted source.