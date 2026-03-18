"""Deterministic recommendation engine for financial insights.

This module is intentionally pure and framework-agnostic.
"""

from __future__ import annotations

from typing import Any


_SEVERITY_WEIGHT = {"high": 3, "medium": 2, "low": 1}


def _as_number(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric")
    return float(value)


def _validate_snapshot(financial_snapshot: dict) -> tuple[float | None, float, list[dict]]:
    if not isinstance(financial_snapshot, dict):
        raise TypeError("financial_snapshot must be a dict")

    if "projected_total" not in financial_snapshot:
        raise ValueError("financial_snapshot must contain 'projected_total'")

    if "category_breakdown" not in financial_snapshot:
        raise ValueError("financial_snapshot must contain 'category_breakdown'")

    projected_total = _as_number(financial_snapshot["projected_total"], "projected_total")
    category_breakdown = financial_snapshot["category_breakdown"]

    if not isinstance(category_breakdown, list):
        raise ValueError("category_breakdown must be a list")

    meta_value_raw = financial_snapshot.get("meta_value")
    meta_value = None
    if meta_value_raw is not None:
        meta_value = _as_number(meta_value_raw, "meta_value")

    for item in category_breakdown:
        if not isinstance(item, dict):
            raise ValueError("each category item must be a dict")

        required_fields = {
            "category",
            "total",
            "percentage",
            "variation_vs_previous_month",
        }
        if not required_fields.issubset(item.keys()):
            raise ValueError("category item is missing required fields")

        if not isinstance(item["category"], str) or not item["category"].strip():
            raise ValueError("category must be a non-empty string")

        _as_number(item["total"], "total")
        _as_number(item["percentage"], "percentage")
        _as_number(item["variation_vs_previous_month"], "variation_vs_previous_month")

    return meta_value, projected_total, category_breakdown


def generate_recommendations(financial_snapshot: dict) -> list[dict]:
    """Generate deterministic recommendations based on financial snapshot."""

    meta_value, projected_total, category_breakdown = _validate_snapshot(financial_snapshot)

    recommendations: list[dict] = []

    # Rule 1: goal overflow alert.
    if meta_value is not None and projected_total > meta_value:
        exceeded = round(projected_total - meta_value, 2)

        top_category = None
        if category_breakdown:
            top_category = max(
                category_breakdown,
                key=lambda item: _as_number(item["total"], "total"),
            )

        category_label = (
            top_category["category"].strip() if top_category is not None else "categoria principal"
        )

        recommendations.append(
            {
                "type": "meta_alert",
                "severity": "high",
                "message": f"Sua projeção excede a meta em R$ {exceeded:.2f}.",
                "action_suggestion": (
                    f"Reduza gastos na categoria {category_label}, que está mais impactante no período."
                ),
            }
        )

    # Rules 2 and 3 with dedup per category.
    alerted_categories: set[str] = set()

    for item in category_breakdown:
        category = item["category"].strip()
        percentage = _as_number(item["percentage"], "percentage")
        variation = _as_number(
            item["variation_vs_previous_month"],
            "variation_vs_previous_month",
        )

        if category in alerted_categories:
            continue

        if percentage > 30:
            recommendations.append(
                {
                    "type": "category_dominance",
                    "severity": "medium",
                    "message": (
                        f"A categoria {category} representa {round(percentage, 2):.2f}% dos gastos."
                    ),
                    "action_suggestion": (
                        f"Considere reduzir 10% dos gastos em {category} no próximo ciclo."
                    ),
                }
            )
            alerted_categories.add(category)
            continue

        if variation > 25:
            recommendations.append(
                {
                    "type": "abnormal_growth",
                    "severity": "medium",
                    "message": (
                        f"A categoria {category} cresceu {round(variation, 2):.2f}% vs mês anterior."
                    ),
                    "action_suggestion": (
                        f"Revise a categoria {category} para identificar aumento fora do padrão."
                    ),
                }
            )
            alerted_categories.add(category)

    recommendations.sort(
        key=lambda item: _SEVERITY_WEIGHT.get(item.get("severity", "low"), 0),
        reverse=True,
    )

    return recommendations
