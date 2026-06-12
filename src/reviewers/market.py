"""Market reviewer agent."""

from __future__ import annotations

from src.core.base_reviewer import BaseReviewer


class MarketReviewer(BaseReviewer):
    """Evaluates the market opportunity and competitive landscape of a project.

    Focus areas include market size, growth trajectory, customer segments,
    positioning, and competitive dynamics.
    """

    reviewer_name: str = "Market"
    prompt_file: str = "market.md"

    def get_focus_areas(self) -> list[str]:
        return [
            "Total addressable market (TAM/SAM/SOM)",
            "Market growth & timing",
            "Customer segmentation",
            "Competitive landscape",
            "Positioning & differentiation",
            "Distribution channels",
        ]
