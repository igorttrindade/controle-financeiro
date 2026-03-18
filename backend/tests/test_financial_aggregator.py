import unittest

from backend.services.financial_aggregator import aggregate_transactions


class FinancialAggregatorTests(unittest.TestCase):
    def test_returns_zeroed_totals_for_empty_list(self):
        result = aggregate_transactions([])

        self.assertEqual(result["total_income"], 0.0)
        self.assertEqual(result["total_expense"], 0.0)
        self.assertEqual(result["balance"], 0.0)

    def test_aggregates_only_income(self):
        data = [
            {"type": "income", "value": 100.0},
            {"type": "income", "value": 50.25},
        ]

        result = aggregate_transactions(data)

        self.assertEqual(result["total_income"], 150.25)
        self.assertEqual(result["total_expense"], 0.0)
        self.assertEqual(result["balance"], 150.25)

    def test_aggregates_only_expense(self):
        data = [
            {"type": "expense", "value": 60.0},
            {"type": "expense", "value": 39.5},
        ]

        result = aggregate_transactions(data)

        self.assertEqual(result["total_income"], 0.0)
        self.assertEqual(result["total_expense"], 99.5)
        self.assertEqual(result["balance"], -99.5)

    def test_aggregates_mixed_transactions(self):
        data = [
            {"type": "income", "value": 1200.0},
            {"type": "expense", "value": 300.0},
            {"type": "income", "value": 49.9},
            {"type": "expense", "value": 100.0},
        ]

        result = aggregate_transactions(data)

        self.assertEqual(result["total_income"], 1249.9)
        self.assertEqual(result["total_expense"], 400.0)
        self.assertEqual(result["balance"], 849.9)

    def test_handles_negative_values_without_breaking(self):
        data = [
            {"type": "income", "value": -100.0},
            {"type": "expense", "value": -20.0},
            {"type": "expense", "value": 30.0},
        ]

        result = aggregate_transactions(data)

        self.assertEqual(result["total_income"], -100.0)
        self.assertEqual(result["total_expense"], 10.0)
        self.assertEqual(result["balance"], -110.0)

    def test_raises_value_error_for_invalid_type(self):
        with self.assertRaises(ValueError):
            aggregate_transactions([{"type": "transfer", "value": 10}])

    def test_raises_value_error_when_required_keys_are_missing(self):
        with self.assertRaises(ValueError):
            aggregate_transactions([{"type": "income"}])

        with self.assertRaises(ValueError):
            aggregate_transactions([{"value": 10}])

    def test_raises_value_error_for_non_numeric_value(self):
        with self.assertRaises(ValueError):
            aggregate_transactions([{"type": "income", "value": "10"}])

        with self.assertRaises(ValueError):
            aggregate_transactions([{"type": "expense", "value": True}])

    def test_raises_type_error_when_input_is_not_a_list(self):
        with self.assertRaises(TypeError):
            aggregate_transactions({"type": "income", "value": 10})

    def test_rounds_output_values_to_two_decimal_places(self):
        data = [
            {"type": "income", "value": 10.005},
            {"type": "expense", "value": 0.335},
        ]

        result = aggregate_transactions(data)

        self.assertEqual(result["total_income"], round(10.005, 2))
        self.assertEqual(result["total_expense"], round(0.335, 2))
        self.assertEqual(result["balance"], round(10.005 - 0.335, 2))


if __name__ == "__main__":
    unittest.main()
