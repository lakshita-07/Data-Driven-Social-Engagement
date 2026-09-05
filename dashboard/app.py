from pathlib import Path

import pandas as pd
import streamlit as st


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


@st.cache_data
def load_csv(filename: str, required: bool = True) -> pd.DataFrame:
    path = PROCESSED_DIR / filename
    if not path.exists():
        if required:
            raise FileNotFoundError(f"Required dashboard file is missing: {path}")
        return pd.DataFrame()
    return pd.read_csv(path)


def format_number(value: float) -> str:
    return f"{value:,.0f}"


st.set_page_config(
    page_title="DDSE Analytics Dashboard",
    page_icon="📊",
    layout="wide",
)

st.title("Data-Driven Social Engagement Initiative")
st.caption("YouTube engagement, audience resonance, and topic performance")

try:
    posts = load_csv("posts_virality.csv")
    topics = load_csv("posts_topics.csv")
    comments = load_csv("comments_relatability.csv")
except FileNotFoundError as error:
    st.error(str(error))
    st.stop()

sentiment = load_csv("comments_sentiment.csv", required=False)
topic_relatability = load_csv("topic_relatability.csv", required=False)
format_analysis = load_csv("format_analysis.csv", required=False)
topic_performance = load_csv("topic_performance.csv", required=False)
recommendations = load_csv("recommendations.csv", required=False)
trend_forecasts = load_csv("trend_forecasts.csv", required=False)
relatability_metrics = load_csv("relatability_model_metrics.csv", required=False)
ab_test_results = load_csv("ab_test_results_summary.csv", required=False)

content_types = ["All"] + sorted(posts["content_type"].dropna().unique().tolist())
selected_format = st.sidebar.selectbox("Content format", content_types)
filtered_posts = posts if selected_format == "All" else posts[posts["content_type"] == selected_format]

st.sidebar.caption("Shares, saves, and retention are unavailable from the public YouTube API.")

total_views = filtered_posts["views"].sum()
average_engagement = filtered_posts["engagement_rate"].mean()
relatable_count = int(comments["relatability"].eq("Relatable").sum())

metric_columns = st.columns(4)
metric_columns[0].metric("Videos", format_number(len(filtered_posts)))
metric_columns[1].metric("Total views", format_number(total_views))
metric_columns[2].metric("Average engagement", f"{average_engagement:.2f}%")
metric_columns[3].metric("Relatable comments", format_number(relatable_count))

st.subheader("Performance overview")
overview_left, overview_right = st.columns(2)
with overview_left:
    st.markdown("**Views by content format**")
    views_by_format = filtered_posts.groupby("content_type")["views"].sum().sort_values(ascending=False)
    st.bar_chart(views_by_format)
with overview_right:
    st.markdown("**Engagement by content format**")
    engagement_by_format = filtered_posts.groupby("content_type")["engagement_rate"].mean().sort_values(ascending=False)
    st.bar_chart(engagement_by_format)

st.subheader("Topic performance and audience resonance")
topic_left, topic_right = st.columns(2)
with topic_left:
    if topic_performance.empty:
        st.info("Run `python3 -m src.models.topic_performance` to generate topic performance data.")
    else:
        topic_view = topic_performance.set_index("topic")[["average_engagement_rate", "average_virality_score"]]
        st.bar_chart(topic_view)
with topic_right:
    if topic_relatability.empty:
        st.info("Run `python3 -m src.models.topic_relatability` to generate topic resonance data.")
    else:
        resonance_view = topic_relatability.set_index("topic")["relatable_comment_rate"]
        st.bar_chart(resonance_view)

if not topic_relatability.empty:
    st.dataframe(topic_relatability, use_container_width=True, hide_index=True)

st.subheader("Historical recommendations")
if recommendations.empty:
    st.info("Run `python3 -m src.models.recommendation_engine` to generate recommendations.")
else:
    selected_recommendation_type = st.selectbox(
        "Recommendation category",
        recommendations["recommendation_type"].dropna().unique(),
    )
    selected_recommendations = recommendations[
        recommendations["recommendation_type"] == selected_recommendation_type
    ].head(5)
    st.dataframe(
        selected_recommendations[
            [
                "recommendation",
                "video_count",
                "average_engagement_rate",
                "average_virality_score",
                "relatable_comment_rate",
                "evidence_note",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )

st.subheader("External trend forecast")
if trend_forecasts.empty:
    st.info(
        "Add real dated keyword history to `data/external/keyword_history.csv`, "
        "then run `python3 -m src.models.trend_forecasting`."
    )
else:
    st.dataframe(trend_forecasts, use_container_width=True, hide_index=True)

st.subheader("Relatability model evaluation")
st.caption(
    "Metrics are meaningful as model evaluation only when the label file has been reviewed by a human."
)
if relatability_metrics.empty:
    st.info(
        "Manually label the annotation sample before reporting classifier metrics. "
        "Run `python3 -m src.nlp.relatability_model` to begin."
    )
else:
    st.dataframe(relatability_metrics, use_container_width=True, hide_index=True)

st.subheader("Controlled A/B test results")
if ab_test_results.empty:
    st.info(
        "Run a controlled content experiment first, then save its observations "
        "to `data/external/ab_test_results.csv` and run `python3 -m src.models.ab_testing`."
    )
else:
    st.dataframe(ab_test_results, use_container_width=True, hide_index=True)

st.subheader("Top videos by virality proxy")
st.caption("Virality is an engagement-based proxy combining engagement rate and view reach; it is not the unavailable share/save viral coefficient.")
top_videos = filtered_posts.sort_values("virality_score", ascending=False).head(10)
st.dataframe(
    top_videos[["post_id", "content_type", "topic" if "topic" in top_videos else "platform", "views", "engagement_rate", "virality_score", "virality_level"]]
    if "topic" in top_videos
    else top_videos[["post_id", "content_type", "platform", "views", "engagement_rate", "virality_score", "virality_level"]],
    use_container_width=True,
    hide_index=True,
)

st.subheader("Comment analysis")
comment_left, comment_right = st.columns(2)
with comment_left:
    sentiment_counts = sentiment["sentiment"].value_counts() if "sentiment" in sentiment else pd.Series(dtype="int64")
    if sentiment_counts.empty:
        st.info("Sentiment data is unavailable.")
    else:
        st.markdown("**Sentiment distribution**")
        st.bar_chart(sentiment_counts)
with comment_right:
    relatability_counts = comments["relatability"].value_counts()
    st.markdown("**Relatability distribution**")
    st.bar_chart(relatability_counts)

st.subheader("Data limitations")
st.info(
    "The dataset is observational, and YouTube counts are current cumulative values. "
    "Format, topic, and posting-time comparisons should not be interpreted as causal A/B tests."
)