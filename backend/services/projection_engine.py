"""Deterministic projection engine for dashboard insights.

Pure domain logic with no framework/database dependency.
"""

from __future__ import annotations

import calendar
from collections import defaultdict
from datetime import date
from typing import Any


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if isinstance(value, bool):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def calculate_projection(
    transactions: list[dict],
    aggregated: dict,
    period: str,
    meta_value: float | None = None,
    reference_date: date | None = None,
) -> dict:
    """Calculate projected monthly expense and category breakdown.

    Args:
        transactions: normalized transaction items.
        aggregated: totals returned by aggregate_transactions.
        period: month label in YYYY-MM format.
        meta_value: optional monthly goal amount.
        reference_date: optional date override used for deterministic tests.
    """

    if reference_date is None:
        reference_date = date.today()

    year, month = (int(part) for part in period.split("-"))
    days_in_month = calendar.monthrange(year, month)[1]

    if reference_date.year == year and reference_date.month == month:
        days_elapsed = max(1, min(reference_date.day, days_in_month))
    else:
        days_elapsed = days_in_month

    total_expense = _safe_float(aggregated.get("total_expense"))
    projected_total = total_expense if days_elapsed <= 0 else (total_expense / days_elapsed) * days_in_month

    category_totals: dict[str, float] = defaultdict(float)
    for item in transactions:
        if not isinstance(item, dict):
            continue
        if item.get("type") != "expense":
            continue
        category = str(item.get("category") or "Outros").strip() or "Outros"
        category_totals[category] += _safe_float(item.get("value"))

    breakdown = []
    for category, total in category_totals.items():
        percentage = 0.0
        if total_expense > 0:
            percentage = (total / total_expense) * 100

        breakdown.append(
            {
                "category": category,
                "total": round(total, 2),
                "percentage": round(percentage, 2),
                # Placeholder deterministic value until previous-month comparison is added.
                "variation_vs_previous_month": 0.0,
            }
        )

    breakdown.sort(key=lambda item: item["total"], reverse=True)

    return {
        "meta_value": None if meta_value is None else round(_safe_float(meta_value), 2),
        "projected_total": round(projected_total, 2),
        "category_breakdown": breakdown,
        "period": period,
        "days_elapsed": days_elapsed,
        "days_in_month": days_in_month,
    }
