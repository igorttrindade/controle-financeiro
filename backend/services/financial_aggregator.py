"""Pure financial aggregation helpers.

This module intentionally has no dependency on Flask, database access,
or side effects so it can be unit-tested in isolation.
"""

from __future__ import annotations


VALID_TRANSACTION_TYPES = {"income", "expense"}


def aggregate_transactions(transactions: list[dict]) -> dict:
    """Aggregate income/expense totals and balance from transaction items.

    Args:
        transactions: List of dictionaries in the format
            {"type": "income" | "expense", "value": number}.

    Returns:
        Dict with rounded totals:
        {
            "total_income": float,
            "total_expense": float,
            "balance": float,
        }

    Raises:
        TypeError: If ``transactions`` is not a list.
        ValueError: If an item has invalid structure/content.
    """

    if not isinstance(transactions, list):
        raise TypeError("transactions must be a list")

    total_income = 0.0
    total_expense = 0.0

    for item in transactions:
        if not isinstance(item, dict):
            raise ValueError("each transaction must be a dict")

        if "type" not in item or "value" not in item:
            raise ValueError("each transaction must contain 'type' and 'value'")

        transaction_type = item["type"]
        value = item["value"]

        if transaction_type not in VALID_TRANSACTION_TYPES:
            raise ValueError("transaction type must be 'income' or 'expense'")

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise ValueError("transaction value must be numeric")

        numeric_value = float(value)

        if transaction_type == "income":
            total_income += numeric_value
        else:
            total_expense += numeric_value

    balance = total_income - total_expense

    return {
        "total_income": round(total_income, 2),
        "total_expense": round(total_expense, 2),
        "balance": round(balance, 2),
    }
