"""Risk reviewer agent."""

from __future__ import annotations

from src.core.base_reviewer import BaseReviewer


class RiskReviewer(BaseReviewer):
    """Evaluates the risk profile and mitigation strategies of a project.

    Focus areas include regulatory compliance, technical risks, business
    continuity, legal exposure, and operational vulnerabilities.
    """

    reviewer_name: str = "Risk"
    prompt_file: str = "risk.md"

    def get_focus_areas(self) -> list[str]:
        return [
            "Regulatory & legal compliance",
            "Data privacy & security risk",
            "Technical failure modes",
            "Key-person & team dependencies",
            "Financial & runway risk",
            "Reputational & ethical risk",
        ]
