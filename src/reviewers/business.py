"""Business reviewer agent."""

from __future__ import annotations

from src.core.base_reviewer import BaseReviewer


class BusinessReviewer(BaseReviewer):
    """Evaluates the business viability and revenue model of a project.

    Focus areas include unit economics, revenue streams, go-to-market
    strategy, competitive moat, and investor attractiveness.
    """

    reviewer_name: str = "Business"
    prompt_file: str = "business.md"

    def get_focus_areas(self) -> list[str]:
        return [
            "Revenue model & monetisation",
            "Unit economics (CAC, LTV, payback)",
            "Go-to-market strategy",
            "Competitive moat",
            "Funding & resource requirements",
            "Financial sustainability",
        ]
