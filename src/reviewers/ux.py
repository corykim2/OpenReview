"""UX reviewer agent."""

from __future__ import annotations

from src.core.base_reviewer import BaseReviewer


class UXReviewer(BaseReviewer):
    """Evaluates the user experience design and usability of a project.

    Focus areas include user journey, onboarding, accessibility,
    interface clarity, and overall product feel.
    """

    reviewer_name: str = "UX"
    prompt_file: str = "ux.md"

    def get_focus_areas(self) -> list[str]:
        return [
            "User journey & onboarding",
            "Interface clarity & simplicity",
            "Accessibility (WCAG compliance)",
            "Error handling & empty states",
            "Mobile responsiveness",
            "Personalisation & delight",
        ]
