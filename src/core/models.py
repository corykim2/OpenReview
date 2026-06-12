"""Core data models for OpenReview."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Project:
    """Represents a project or idea proposal to be reviewed.

    Attributes:
        title: The name of the project or idea.
        description: A detailed description of the project.
        target_users: List of intended user segments.
        business_model: The monetization or business strategy.
        raw_data: The original parsed input data dict.
    """

    title: str
    description: str
    target_users: list[str] = field(default_factory=list)
    business_model: str = ""
    raw_data: dict[str, Any] = field(default_factory=dict, repr=False)

    def to_context_string(self) -> str:
        """Format project data as a readable context string for prompts."""
        lines = [
            f"Project Title: {self.title}",
            f"\nDescription:\n{self.description}",
        ]
        if self.target_users:
            lines.append(f"\nTarget Users: {', '.join(self.target_users)}")
        if self.business_model:
            lines.append(f"\nBusiness Model: {self.business_model}")

        extra_fields = {
            k: v
            for k, v in self.raw_data.items()
            if k not in {"title", "description", "target_users", "business_model"}
        }
        if extra_fields:
            lines.append("\nAdditional Information:")
            for key, value in extra_fields.items():
                lines.append(f"  {key}: {value}")

        return "\n".join(lines)


@dataclass
class ReviewResult:
    """The structured result from a single reviewer agent.

    Attributes:
        reviewer_name: Human-readable name of the reviewer (e.g. "Technology").
        score: Numeric score from 0.0 to 10.0.
        summary: One-paragraph executive summary of the review.
        strengths: Positive aspects identified by the reviewer.
        weaknesses: Negative aspects or gaps identified.
        recommendations: Actionable suggestions for improvement.
        raw_response: The unprocessed text response from the AI.
    """

    reviewer_name: str
    score: float
    summary: str
    strengths: list[str] = field(default_factory=list)
    weaknesses: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    raw_response: str = field(default="", repr=False)

    def __post_init__(self) -> None:
        if not 0.0 <= self.score <= 10.0:
            raise ValueError(
                f"Score must be between 0.0 and 10.0, got {self.score}"
            )


@dataclass
class ReportData:
    """Aggregated data for the final Markdown report.

    Attributes:
        project: The project that was reviewed.
        results: All individual reviewer results.
        overall_score: Computed average across all reviewers.
    """

    project: Project
    results: list[ReviewResult] = field(default_factory=list)

    @property
    def overall_score(self) -> float:
        """Return the arithmetic mean of all reviewer scores."""
        if not self.results:
            return 0.0
        return round(sum(r.score for r in self.results) / len(self.results), 2)

    @property
    def all_recommendations(self) -> list[str]:
        """Deduplicated flat list of every recommendation from all reviewers."""
        seen: set[str] = set()
        unique: list[str] = []
        for result in self.results:
            for rec in result.recommendations:
                if rec not in seen:
                    seen.add(rec)
                    unique.append(rec)
        return unique
