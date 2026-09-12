import unittest

import pandas as pd

from src.models.virality_analysis import calculate_virality_score


class MetricTests(unittest.TestCase):
    def test_weighted_virality_score(self):
        posts = pd.DataFrame(
            {
                "views": [1000],
                "likes": [100],
                "comments_count": [20],
                "shares": [10],
                "saves": [5],
                "engagement_rate": [12],
            }
        )
        result = calculate_virality_score(posts)
        self.assertAlmostEqual(result.loc[0, "virality_score"], 1.95)

    def test_youtube_proxy_handles_missing_share_and_save_counts(self):
        posts = pd.DataFrame(
            {
                "views": [1000, 2000],
                "likes": [100, 200],
                "comments_count": [20, 30],
                "engagement_rate": [12, 11.5],
            }
        )
        result = calculate_virality_score(posts)
        self.assertTrue(result["virality_score"].ge(0).all())
        self.assertTrue(
            result["virality_score_type"].eq("YouTube engagement-reach proxy").all()
        )


if __name__ == "__main__":
    unittest.main()
