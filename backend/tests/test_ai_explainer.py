import unittest

from backend.services.ai_explainer import generate_natural_summary


class AIExplainerTests(unittest.TestCase):
    def test_prioritizes_goal_alert_when_high_severity_meta_exists(self):
        snapshot = {
            "meta_value": 1000.0,
            "projected_total": 1300.0,
            "category_breakdown": [],
        }
        recommendations = [
            {
                "type": "meta_alert",
                "severity": "high",
                "message": "A projecao excede a meta em R$ 300,00.",
                "action_suggestion": "Reduza gastos em Moradia.",
            },
            {
                "type": "category_dominance",
                "severity": "medium",
                "message": "Moradia esta dominante.",
                "action_suggestion": "Corte 10% em Moradia.",
            },
        ]

        summary = generate_natural_summary(snapshot, recommendations)
        first_line = summary.splitlines()[0]

        self.assertIn("Alerta prioritario", first_line)
        self.assertIn("excede", first_line)
        self.assertIn("Reduza gastos em Moradia", summary)

    def test_builds_summary_for_category_dominance_only(self):
        snapshot = {
            "meta_value": 2000.0,
            "projected_total": 1200.0,
            "category_breakdown": [],
        }
        recommendations = [
            {
                "type": "category_dominance",
                "severity": "medium",
                "message": "Lazer representa 35%.",
                "action_suggestion": "Considere reduzir 10% em Lazer.",
            }
        ]

        summary = generate_natural_summary(snapshot, recommendations)

        self.assertIn("Meta mensal", summary)
        self.assertIn("Acoes recomendadas", summary)
        self.assertIn("Considere reduzir 10% em Lazer", summary)

    def test_returns_positive_stability_message_when_no_recommendations(self):
        snapshot = {
            "meta_value": 1500.0,
            "projected_total": 900.0,
            "category_breakdown": [],
        }

        summary = generate_natural_summary(snapshot, [])

        self.assertIn("Panorama estavel", summary)
        self.assertIn("equilibrio financeiro", summary)

    def test_handles_missing_meta_value(self):
        snapshot = {
            "meta_value": None,
            "projected_total": 780.5,
            "category_breakdown": [],
        }
        recommendations = [
            {
                "type": "abnormal_growth",
                "severity": "medium",
                "message": "Transporte cresceu 30%.",
                "action_suggestion": "Revise Transporte ainda esta semana.",
            }
        ]

        summary = generate_natural_summary(snapshot, recommendations)

        self.assertIn("nao definiu uma meta mensal", summary)
        self.assertIn("R$ 780,50", summary)
        self.assertIn("Revise Transporte", summary)


if __name__ == "__main__":
    unittest.main()
