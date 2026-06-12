"""Technology reviewer agent."""

from __future__ import annotations

from src.core.base_reviewer import BaseReviewer


class TechnologyReviewer(BaseReviewer):
    """Evaluates the technical feasibility and architecture of a project.

    Focus areas include tech stack choices, scalability, security,
    infrastructure requirements, and engineering complexity.
    """

    reviewer_name: str = "Technology"
    prompt_file: str = "technology.md"

    def get_focus_areas(self) -> list[str]:
        return [
            "Technical feasibility",
            "Architecture & scalability",
            "Security considerations",
            "Technology stack appropriateness",
            "Engineering complexity & timeline",
            "Infrastructure requirements",
        ]
