import unittest

from src.nlp.relatability_analysis import (
    calculate_relatability_score,
    classify_relatability,
)
from src.preprocessing.data_preprocessing import clean_comment


class NLPTests(unittest.TestCase):
    def test_relatable_phrase_is_classified(self):
        score = calculate_relatability_score("This is literally me")
        self.assertEqual(classify_relatability(score), "Relatable")

    def test_generic_praise_is_not_automatically_relatable(self):
        score = calculate_relatability_score("Great video, thank you")
        self.assertEqual(classify_relatability(score), "Neutral")

    def test_empty_comment_is_removed_by_cleaner(self):
        self.assertEqual(clean_comment(None), "")
        self.assertEqual(clean_comment("   "), "")


if __name__ == "__main__":
    unittest.main()
