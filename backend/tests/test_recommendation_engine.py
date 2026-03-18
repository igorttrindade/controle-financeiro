import unittest

from backend.services.recommendation_engine import generate_recommendations


class RecommendationEngineTests(unittest.TestCase):
    def test_meta_overflow_generates_high_severity_alert(self):
        snapshot = {
            "meta_value": 1000.0,
            "projected_total": 1200.75,
            "category_breakdown": [
                {
                    "category": "Moradia",
                    "total": 600.0,
                    "percentage": 40.0,
                    "variation_vs_previous_month": 10.0,
                }
            ],
        }

        recommendations = generate_recommendations(snapshot)

        self.assertGreaterEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]["type"], "meta_alert")
        self.assertEqual(recommendations[0]["severity"], "high")
        self.assertIn("R$ 200.75", recommendations[0]["message"])

    def test_category_dominance_generates_medium_alert(self):
        snapshot = {
            "meta_value": 2000.0,
            "projected_total": 1000.0,
            "category_breakdown": [
                {
                    "category": "Lazer",
                    "total": 350.0,
                    "percentage": 35.5,
                    "variation_vs_previous_month": 5.0,
                }
            ],
        }

        recommendations = generate_recommendations(snapshot)

        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]["type"], "category_dominance")
        self.assertEqual(recommendations[0]["severity"], "medium")

    def test_abnormal_growth_generates_medium_alert(self):
        snapshot = {
            "meta_value": 3000.0,
            "projected_total": 1000.0,
            "category_breakdown": [
                {
                    "category": "Transporte",
                    "total": 200.0,
                    "percentage": 20.0,
                    "variation_vs_previous_month": 30.2,
                }
            ],
        }

        recommendations = generate_recommendations(snapshot)

        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]["type"], "abnormal_growth")
        self.assertEqual(recommendations[0]["severity"], "medium")

    def test_multiple_alerts_are_combined_and_sorted_by_severity(self):
        snapshot = {
            "meta_value": 800.0,
            "projected_total": 1200.0,
            "category_breakdown": [
                {
                    "category": "Moradia",
                    "total": 500.0,
                    "percentage": 45.0,
                    "variation_vs_previous_month": 30.0,
                },
                {
                    "category": "Saude",
                    "total": 180.0,
                    "percentage": 20.0,
                    "variation_vs_previous_month": 40.0,
                },
            ],
        }

        recommendations = generate_recommendations(snapshot)

        self.assertEqual(len(recommendations), 3)
        self.assertEqual(recommendations[0]["severity"], "high")
        self.assertEqual(recommendations[0]["type"], "meta_alert")

        types = [item["type"] for item in recommendations]
        self.assertIn("category_dominance", types)
        self.assertIn("abnormal_growth", types)

        # No duplicate recommendation for the same category in category-based rules.
        moradia_count = sum(
            1
            for item in recommendations
            if item["type"] in {"category_dominance", "abnormal_growth"}
            and (
                "Moradia" in item["message"]
                or "Moradia" in item["action_suggestion"]
            )
        )
        self.assertEqual(moradia_count, 1)

    def test_returns_empty_list_when_no_rule_matches(self):
        snapshot = {
            "meta_value": 2000.0,
            "projected_total": 1000.0,
            "category_breakdown": [
                {
                    "category": "Educacao",
                    "total": 100.0,
                    "percentage": 10.0,
                    "variation_vs_previous_month": 5.0,
                }
            ],
        }

        recommendations = generate_recommendations(snapshot)

        self.assertEqual(recommendations, [])

    def test_handles_meta_value_none_without_meta_alert(self):
        snapshot = {
            "meta_value": None,
            "projected_total": 5000.0,
            "category_breakdown": [
                {
                    "category": "Alimentacao",
                    "total": 2000.0,
                    "percentage": 40.0,
                    "variation_vs_previous_month": 10.0,
                }
            ],
        }

        recommendations = generate_recommendations(snapshot)

        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0]["type"], "category_dominance")


if __name__ == "__main__":
    unittest.main()
