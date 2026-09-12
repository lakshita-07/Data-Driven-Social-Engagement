import unittest

from src.models.ab_framework_validation import simulate
from src.models.ab_testing import analyze_ab_tests


class ABFrameworkValidationTests(unittest.TestCase):
    def test_framework_detects_known_effect(self):
        summary = analyze_ab_tests(simulate(effect=1.5, seed=0))
        self.assertTrue(summary.loc[0, "statistically_significant"])

    def test_framework_does_not_mark_identical_seeded_groups_significantly(self):
        summary = analyze_ab_tests(simulate(effect=0.0, seed=0))
        self.assertFalse(summary.loc[0, "statistically_significant"])


if __name__ == "__main__":
    unittest.main()
