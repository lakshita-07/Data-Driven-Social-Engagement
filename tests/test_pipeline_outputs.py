import unittest
from pathlib import Path

import pandas as pd

from src.models.ab_testing import analyze_ab_tests
from src.models.trend_forecasting import forecast_keyword_trends


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"


class PipelineOutputTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.posts = pd.read_csv(PROCESSED_DIR / "posts_topics.csv")
        cls.comments = pd.read_csv(PROCESSED_DIR / "comments_relatability.csv")
        cls.topic_relatability = pd.read_csv(
            PROCESSED_DIR / "topic_relatability.csv"
        )
        cls.recommendations = pd.read_csv(PROCESSED_DIR / "recommendations.csv")

    def test_post_ids_are_unique_and_comment_links_are_valid(self):
        self.assertFalse(self.posts["post_id"].duplicated().any())
        self.assertTrue(self.comments["post_id"].isin(self.posts["post_id"]).all())

    def test_expected_dataset_counts_are_preserved(self):
        self.assertEqual(len(self.posts), 107)
        self.assertEqual(len(self.comments), 8841)
        self.assertEqual(
            int(self.comments["relatability"].eq("Relatable").sum()),
            643,
        )

    def test_topic_relatability_reconciles_with_comments(self):
        self.assertEqual(
            int(self.topic_relatability["comment_count"].sum()),
            len(self.comments),
        )
        self.assertEqual(
            int(self.topic_relatability["relatable_comment_count"].sum()),
            int(self.comments["relatability"].eq("Relatable").sum()),
        )
        self.assertTrue(
            self.topic_relatability["relatable_comment_rate"].between(0, 100).all()
        )

    def test_unavailable_youtube_metrics_are_not_invented(self):
        for column in ("shares", "saves", "retention_rate"):
            self.assertTrue(self.posts[column].isna().all(), column)

    def test_recommendations_have_required_categories_and_evidence(self):
        required_categories = {"Topic", "Format", "Posting hour", "Posting day"}
        self.assertTrue(
            required_categories.issubset(
                set(self.recommendations["recommendation_type"])
            )
        )
        self.assertTrue(
            self.recommendations["recommendation_score"].notna().all()
        )
        self.assertTrue(self.recommendations["evidence_note"].str.len().gt(0).all())

    def test_ab_testing_identifies_a_clear_variant_difference(self):
        results = pd.DataFrame(
            {
                "experiment_id": ["hook"] * 6,
                "variant": ["A", "A", "A", "B", "B", "B"],
                "metric_name": ["engagement_rate"] * 6,
                "metric_value": [1, 1, 1, 5, 5, 5],
            }
        )
        summary = analyze_ab_tests(results)
        self.assertEqual(summary.loc[0, "winner_by_mean"], "B")
        self.assertTrue(summary.loc[0, "statistically_significant"])

    def test_trend_forecasting_detects_rising_keyword(self):
        history = pd.DataFrame(
            {
                "keyword": ["burnout"] * 6,
                "date": pd.date_range("2026-01-01", periods=6),
                "volume": [100, 110, 120, 150, 180, 220],
            }
        )
        forecast = forecast_keyword_trends(history)
        self.assertEqual(forecast.loc[0, "trend"], "Rising")


if __name__ == "__main__":
    unittest.main()