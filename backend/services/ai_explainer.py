"""Deterministic natural-language explainer for financial projections.

This module is pure and framework-agnostic. It is intentionally built around
static templates so the implementation can be swapped for an LLM provider in a
future integration layer.
"""

from __future__ import annotations

from typing import Any


def _format_currency(value: float) -> str:
    """Format value as BRL currency with two decimals."""
    numeric = float(value)
    formatted = f"{numeric:,.2f}"
    formatted = formatted.replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"


def _build_meta_message(projection_snapshot: dict, recommendations: list[dict]) -> str | None:
    """Build the leading message prioritizing high-severity goal alerts."""
    high_meta_alert = next(
        (
            rec
            for rec in recommendations
            if rec.get("type") == "meta_alert" and rec.get("severity") == "high"
        ),
        None,
    )

    if high_meta_alert is not None:
        return f"Alerta prioritario: {high_meta_alert.get('message', 'Sua meta mensal foi excedida.')}"

    meta_value = projection_snapshot.get("meta_value")
    projected_total = projection_snapshot.get("projected_total")

    if meta_value is None:
        if isinstance(projected_total, (int, float)) and not isinstance(projected_total, bool):
            return (
                "Voce ainda nao definiu uma meta mensal. "
                f"Sua projecao atual esta em {_format_currency(float(projected_total))}."
            )
        return "Voce ainda nao definiu uma meta mensal."

    if isinstance(meta_value, (int, float)) and not isinstance(meta_value, bool):
        if isinstance(projected_total, (int, float)) and not isinstance(projected_total, bool):
            return (
                f"Meta mensal: {_format_currency(float(meta_value))}. "
                f"Projecao atual: {_format_currency(float(projected_total))}."
            )
        return f"Meta mensal configurada em {_format_currency(float(meta_value))}."

    return None


def _build_recommendation_section(recommendations: list[dict]) -> list[str]:
    """Create recommendation lines from action suggestions."""
    if not recommendations:
        return [
            "Panorama estavel: nao encontramos sinais criticos no periodo analisado.",
            "Mantenha o acompanhamento regular para preservar seu equilibrio financeiro.",
        ]

    lines: list[str] = ["Acoes recomendadas para o proximo ciclo:"]

    for rec in recommendations:
        action = str(rec.get("action_suggestion", "")).strip()
        if action:
            lines.append(f"- {action}")

    if len(lines) == 1:
        lines.append("- Continue monitorando suas categorias para manter consistencia.")

    return lines


def generate_natural_summary(
    projection_snapshot: dict,
    recommendations: list[dict],
) -> str:
    """Generate deterministic assistant-style summary in up to 5-6 lines."""
    if not isinstance(projection_snapshot, dict):
        raise TypeError("projection_snapshot must be a dict")
    if not isinstance(recommendations, list):
        raise TypeError("recommendations must be a list")

    severity_order = {"high": 3, "medium": 2, "low": 1}
    sorted_recommendations = sorted(
        [rec for rec in recommendations if isinstance(rec, dict)],
        key=lambda item: severity_order.get(str(item.get("severity", "low")), 0),
        reverse=True,
    )

    lines: list[str] = []

    meta_line = _build_meta_message(projection_snapshot, sorted_recommendations)
    if meta_line:
        lines.append(meta_line)

    recommendation_lines = _build_recommendation_section(sorted_recommendations)
    lines.extend(recommendation_lines)

    # Keep output concise: max 6 lines.
    return "\n".join(lines[:6])
